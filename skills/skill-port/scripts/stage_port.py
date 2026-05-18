#!/usr/bin/env python3
"""Stage a target-agent port without installing it.

Security boundary:
- does not install skills/plugins
- does not execute source scripts, package managers, hooks, or plugin commands
- does not make network requests
- writes only under the requested output root
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

import audit_skill


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage an audited skill/plugin port without installing it.")
    parser.add_argument("source", help="Path to a skill, plugin, or repository folder")
    parser.add_argument("--target-agent", default="codex", help="Target agent name. Defaults to codex.")
    parser.add_argument("--output-root", default=".", help="Directory where ports/ or skills/ should be created.")
    parser.add_argument("--clean", action="store_true", help="Remove an existing staged output directory before writing.")
    return parser.parse_args()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-") or "item"


def read_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].splitlines()
    body_start = text.find("\n", end + 4)
    body = text[body_start + 1 :] if body_start != -1 else ""
    data: dict[str, str] = {}
    current_key = ""
    for line in raw:
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip().strip("'\"")
        elif current_key:
            data[current_key] = f"{data[current_key]} {line.strip()}".strip()
    return data, body


def write_skill(src: Path, dst: Path, name: str | None = None, prefix_note: str | None = None) -> None:
    if dst.parent.exists() and dst.parent.is_dir():
        shutil.rmtree(dst.parent)
    shutil.copytree(src.parent, dst.parent)
    text = src.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = read_frontmatter(text)
    skill_name = name or slug(dst.parent.name)
    description = re.sub(r"\s+", " ", frontmatter.get("description", f"Ported skill {skill_name}")).strip()
    if prefix_note:
        body = f"{prefix_note.rstrip()}\n\n{body.lstrip()}"
    dst.write_text(f"---\nname: {skill_name}\ndescription: {description}\n---\n{body}", encoding="utf-8")


def title_from_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith("#"):
            return line.strip("# ").strip()
    return path.stem


def frontmatter_field(path: Path, field: str) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, _ = read_frontmatter(text)
    return frontmatter.get(field, "")


def append_command_map(path: Path, source_root: Path, command_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# Command Map\n\n"
            "Source slash commands are represented as plugin workflow entrypoints. "
            "Use these command names in natural language or through the bundled router skill.\n\n",
            encoding="utf-8",
        )
    rel = command_path.relative_to(source_root).as_posix()
    description = frontmatter_field(command_path, "description") or title_from_markdown(command_path)
    argument_hint = frontmatter_field(command_path, "argument-hint")
    suffix = f" Inputs: `{argument_hint}`." if argument_hint else ""
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"- `{rel}` -> {description}.{suffix}\n")


def command_name(command_path: Path) -> str:
    frontmatter_name = frontmatter_field(command_path, "name")
    return slug(frontmatter_name or command_path.stem)


def command_description(command_path: Path) -> str:
    return re.sub(
        r"\s+",
        " ",
        frontmatter_field(command_path, "description") or title_from_markdown(command_path),
    ).strip()


def command_metadata(commands: list[Path]) -> dict[str, str]:
    for command in commands:
        text = command.read_text(encoding="utf-8", errors="replace")
        frontmatter, _ = read_frontmatter(text)
        for key in ("creator", "author"):
            value = frontmatter.get(key, "").strip()
            if value:
                return {key: value}
    return {}


def contributor_from_manifest(source_manifest: dict[str, Any], commands: list[Path] | None = None) -> tuple[dict[str, Any] | str | None, str]:
    contributor = source_manifest.get("creator") or source_manifest.get("author")
    if not contributor and commands:
        metadata = command_metadata(commands)
        contributor = metadata.get("creator") or metadata.get("author")
    if isinstance(contributor, dict):
        name = str(contributor.get("name") or "Source Metadata Unavailable").strip()
    elif isinstance(contributor, str):
        name = contributor.strip()
    else:
        name = "Source Metadata Unavailable"
    return contributor, name or "Source Metadata Unavailable"


def plugin_root_for(path: Path) -> Path | None:
    parts = path.parts
    if ".codex-plugin" in parts:
        return Path(*parts[: parts.index(".codex-plugin")])
    if "references" in parts:
        return Path(*parts[: parts.index("references")])
    if "skills" in parts:
        return Path(*parts[: parts.index("skills")])
    if "hooks" in parts:
        return Path(*parts[: parts.index("hooks")])
    return None


def codex_plugin_name(plugin_root: Path, source_manifest: dict[str, Any] | None = None) -> str:
    manifest_name = source_manifest.get("name") if source_manifest else None
    if isinstance(manifest_name, str) and manifest_name.strip():
        return slug(manifest_name)
    if plugin_root.name in {"codex-plugin", "codex-marketplace"} and plugin_root.parent.name:
        return slug(plugin_root.parent.name)
    return slug(plugin_root.name)


def write_command_workflow_skill(plugin_root: Path, source_root: Path, commands: list[Path]) -> Path:
    plugin_name = codex_plugin_name(plugin_root)
    display_name = re.sub(r"[-_]+", " ", plugin_name).strip().title() or "Command Workflow"
    skill_dir = plugin_root / "skills" / plugin_name
    skill_path = skill_dir / "SKILL.md"
    skill_dir.mkdir(parents=True, exist_ok=True)

    descriptions = [command_description(command) for command in commands]
    primary_description = descriptions[0] if descriptions else f"Run workflows ported from {display_name} commands."
    command_lines = []
    for command in commands:
        rel = command.relative_to(source_root).as_posix()
        name = command_name(command)
        description = command_description(command)
        argument_hint = frontmatter_field(command, "argument-hint")
        input_text = f" Inputs: `{argument_hint}`." if argument_hint else ""
        command_lines.append(f"- `{name}` from `{rel}`: {description}.{input_text}")

    body = (
        f"# {display_name}\n\n"
        "This skill exposes workflows ported from source slash commands. Use the command names "
        "as natural-language triggers; do not assume the source agent's slash-command runtime, "
        "dynamic context injection, tool allowlists, or automatic command execution are available.\n\n"
        "## Safety Rules\n\n"
        "- Treat source command files as instructions, not executable scripts.\n"
        "- Do not run broad repository scans or high-output commands without asking the user first.\n"
        "- Do not read secret files. Report `.env*`, private keys, and credential-like files by path only.\n"
        "- Prefer bounded `rg --files` and targeted file reads over unbounded recursive output.\n\n"
        "## Ported Commands\n\n"
        + "\n".join(command_lines)
        + "\n\n"
        "## Workflow\n\n"
        "1. Identify which ported command the user wants to run from their request.\n"
        "2. Read `references/command-map.md` and the preserved source command reference when needed.\n"
        "3. Convert source command placeholders or argument hints into explicit input handling; ask only for missing required inputs.\n"
        "4. Execute the workflow using target-agent tools and local project instructions.\n"
        "5. Preserve the source command's expected deliverable, but adapt unsafe or source-specific behavior into explicit reviewed steps.\n"
    )
    skill_path.write_text(
        f"---\nname: {plugin_name}\ndescription: {primary_description}\n---\n\n{body}",
        encoding="utf-8",
    )
    return skill_path


def write_agent_workflow(source_root: Path, src: Path, dst: Path) -> None:
    text = src.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = read_frontmatter(text)
    name = slug(dst.parent.name)
    description = frontmatter.get("description", f"Workflow ported from {src.relative_to(source_root).as_posix()}")
    note = (
        "This workflow was ported from a source agent prompt. Automatic dispatch, "
        "managed-agent handoff, and isolated source tool permissions are not installed; "
        "treat them as execution guidance and preserve review checkpoints.\n\n"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(f"---\nname: {name}\ndescription: {description}\n---\n{note}{body}", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def write_codex_manifest(src: Path | None, dst: Path, *, commands: list[Path] | None = None) -> None:
    source_manifest = load_json(src) if src else {}
    plugin_root = dst.parents[1]
    plugin_name = codex_plugin_name(plugin_root, source_manifest)
    description = source_manifest.get("description") or f"Ported plugin {plugin_root.name}"
    contributor, developer_name = contributor_from_manifest(source_manifest, commands)
    manifest: dict[str, Any] = {
        "name": plugin_name,
        "version": str(source_manifest.get("version") or "0.1.0"),
        "description": description,
        "skills": "./skills/",
        "interface": {
            "displayName": re.sub(r"[-_]+", " ", plugin_name).strip().title(),
            "shortDescription": description[:120],
            "longDescription": description,
            "developerName": developer_name,
            "category": "Productivity",
            "capabilities": ["Read", "Write"],
            "defaultPrompt": [f"Use {re.sub(r'[-_]+', ' ', plugin_name).strip().title()}."],
        },
    }
    if commands and not source_manifest.get("description"):
        descriptions = [command_description(command) for command in commands]
        if descriptions:
            manifest["description"] = descriptions[0]
            manifest["interface"]["shortDescription"] = descriptions[0][:120]
            manifest["interface"]["longDescription"] = descriptions[0]
            manifest["interface"]["defaultPrompt"] = [
                f"Use {plugin_name} to run the {command_name(commands[0])} workflow."
            ]
    if (plugin_root / ".mcp.json").exists():
        manifest["mcpServers"] = "./.mcp.json"
    if (plugin_root / ".app.json").exists():
        manifest["apps"] = "./.app.json"
    if (plugin_root / "hooks" / "hooks.json").exists():
        manifest["hooks"] = "./hooks/hooks.json"
    for key in ("creator", "author"):
        if source_manifest.get(key):
            manifest[key] = source_manifest[key]
    if contributor and not manifest.get("creator") and not manifest.get("author"):
        manifest["creator"] = contributor
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_marketplace(report: dict[str, Any], output_root: Path, target: Path) -> None:
    source_name = report["source"]["name"]
    display_name = re.sub(r"[-_]+", " ", source_name).strip().title() or "Local Plugins"
    plugins: dict[str, dict[str, Any]] = {}
    for item in report["porting_map"]:
        target_path = Path(item["target"])
        parts = target_path.parts
        if "plugins" not in parts:
            continue
        plugin_indices = [i for i, part in enumerate(parts) if part == "plugins" and (i == 0 or parts[i - 1] != ".agents")]
        if not plugin_indices:
            continue
        idx = plugin_indices[-1]
        if len(parts) <= idx + 1:
            continue
        plugin = parts[idx + 1]
        plugins[plugin] = {
            "name": plugin,
            "source": {
                "source": "local",
                "path": f"./plugins/{plugin}",
            },
            "policy": {
                "installation": "AVAILABLE",
                "authentication": "ON_USE",
            },
            "category": "Productivity",
        }
    target.parent.mkdir(parents=True, exist_ok=True)
    marketplace = {
        "name": source_name,
        "interface": {
            "displayName": display_name,
        },
        "plugins": sorted(plugins.values(), key=lambda x: x["name"]),
    }
    target.write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")


def copy_json(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    parsed = load_json(src)
    if parsed:
        dst.write_text(json.dumps(parsed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        shutil.copy2(src, dst)


def copy_command_reference(source_root: Path, command_path: Path, plugin_root: Path) -> Path:
    rel = command_path.relative_to(source_root)
    ref = plugin_root / "references" / "source-commands" / rel.with_suffix(".md")
    ref.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(command_path, ref)
    return ref


def output_base(report: dict[str, Any]) -> str:
    layout = report["recommendation"].get("proposed_target_layout")
    if layout:
        return layout.rstrip("/")
    source = report["source"]["name"]
    target = report["target_agent"]
    return f"ports/{source}/{target}"


def main() -> int:
    args = parse_args()
    source_root = Path(args.source).resolve()
    target_agent, inferred = audit_skill.infer_target_agent(args.target_agent)
    report = audit_skill.audit(source_root, target_agent, inferred, "port")
    root = Path(args.output_root).resolve()
    base = root / output_base(report)
    if args.clean and base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    deferred_marketplaces: list[Path] = []
    deferred_manifests: list[tuple[Path, Path]] = []
    commands_by_plugin_root: dict[Path, list[Path]] = {}
    manifest_roots: set[Path] = set()

    for item in report["porting_map"]:
        src = source_root / item["source"]
        dst = root / item["target"]
        action = item["action"]
        if action == "port-skill":
            write_skill(src, dst, name=slug(dst.parent.name))
            written.append(str(dst))
        elif action == "adapt-command-entrypoint":
            append_command_map(dst, source_root, src)
            written.append(str(dst))
            root_for_command = plugin_root_for(dst)
            if target_agent == "codex" and root_for_command is not None:
                commands_by_plugin_root.setdefault(root_for_command, []).append(src)
                written.append(str(copy_command_reference(source_root, src, root_for_command)))
        elif action == "adapt-agent-workflow":
            write_agent_workflow(source_root, src, dst)
            written.append(str(dst))
        elif action == "adapt-plugin-manifest":
            if dst.name == "marketplace.json":
                deferred_marketplaces.append(dst)
            else:
                deferred_manifests.append((src, dst))
        elif action == "adapt-mcp-setup":
            copy_json(src, dst)
            setup = dst.parent / "references" / "mcp-setup.md"
            setup.parent.mkdir(parents=True, exist_ok=True)
            setup.write_text(
                "# MCP Setup\n\n"
                "MCP declarations were staged but not enabled. Configure credentials, subscriptions, "
                "and server access outside the plugin package before relying on these tools.\n",
                encoding="utf-8",
            )
            written.extend([str(dst), str(setup)])
        elif action == "record-empty-hook":
            copy_json(src, dst)
            written.append(str(dst))
        elif action == "adapt-hook-behavior":
            note = dst.parent / "references" / "hook-migration.md" if dst.name == "hooks.json" else dst
            note.parent.mkdir(parents=True, exist_ok=True)
            note.write_text(
                f"# Hook Migration\n\nSource hook `{item['source']}` requires schema and safety review before activation.\n",
                encoding="utf-8",
            )
            written.append(str(note))
        elif action == "adapt-project-instructions":
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            written.append(str(dst))

    for src, dst in deferred_manifests:
        root_for_manifest = plugin_root_for(dst)
        commands = commands_by_plugin_root.get(root_for_manifest, []) if root_for_manifest else []
        write_codex_manifest(src, dst, commands=commands)
        if root_for_manifest:
            manifest_roots.add(root_for_manifest)
        written.append(str(dst))
    for plugin_root, commands in commands_by_plugin_root.items():
        workflow_skill = write_command_workflow_skill(plugin_root, source_root, commands)
        written.append(str(workflow_skill))
        manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
        if plugin_root not in manifest_roots and not manifest_path.exists():
            write_codex_manifest(None, manifest_path, commands=commands)
            written.append(str(manifest_path))
    for dst in deferred_marketplaces:
        write_marketplace(report, root, dst)
        written.append(str(dst))
    synthetic_marketplace = base / ".agents" / "plugins" / "marketplace.json"
    if target_agent == "codex" and base.name == "codex-marketplace" and not synthetic_marketplace.exists():
        write_marketplace(report, root, synthetic_marketplace)
        written.append(str(synthetic_marketplace))

    report["locations"]["output_path"] = str(base)
    if (base / ".agents" / "plugins" / "marketplace.json").exists():
        install_note = (
            "Staged only. To expose this Codex marketplace, review the files, then run "
            f"`codex plugin marketplace add {base}`. Stop there, restart Codex, then install and enable desired plugins "
            "from Codex's plugin directory or another official Codex UI/command when available. Do not hand-edit "
            "`~/.codex/config.toml` plugin enablement entries as a substitute for installation. For explicit Codex "
            "Desktop local testing, use `scripts/install_codex_local_bundle.py <staged-codex-marketplace>`."
        )
    elif (base / ".codex-plugin" / "plugin.json").exists():
        install_note = (
            "Staged only. Add the plugin to a Codex marketplace, then run "
            "`codex plugin marketplace add <marketplace-root>`. Stop there, restart Codex, then install and enable "
            "the plugin from Codex's plugin directory or another official Codex UI/command when available. Do not "
            "hand-edit `~/.codex/config.toml` plugin enablement entries as a substitute for installation. For explicit "
            "Codex Desktop local testing, use `scripts/install_codex_local_bundle.py <staged-codex-marketplace>`."
        )
    else:
        install_note = "Staged only. Install with the target agent's normal skill installer after reviewing generated files."
    stage_report = {
        "source": str(source_root),
        "target_agent": target_agent,
        "output_path": str(base),
        "written_count": len(set(written)),
        "written": sorted(set(written)),
        "audit": report,
        "install_note": install_note,
    }
    (base / "STAGE_REPORT.json").write_text(json.dumps(stage_report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: stage_report[k] for k in ["source", "target_agent", "output_path", "written_count", "install_note"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
