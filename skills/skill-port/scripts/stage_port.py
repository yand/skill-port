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


def write_codex_manifest(src: Path, dst: Path) -> None:
    source_manifest = load_json(src)
    plugin_root = dst.parents[1]
    plugin_name = slug(plugin_root.name)
    description = source_manifest.get("description") or f"Ported plugin {plugin_root.name}"
    author = source_manifest.get("author")
    if isinstance(author, dict):
        developer_name = author.get("name") or "Ported Plugin"
    elif isinstance(author, str):
        developer_name = author
    else:
        developer_name = "Ported Plugin"
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
    if (plugin_root / ".mcp.json").exists():
        manifest["mcpServers"] = "./.mcp.json"
    if (plugin_root / ".app.json").exists():
        manifest["apps"] = "./.app.json"
    if (plugin_root / "hooks" / "hooks.json").exists():
        manifest["hooks"] = "./hooks/hooks.json"
    if author:
        manifest["author"] = author
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
        write_codex_manifest(src, dst)
        written.append(str(dst))
    for dst in deferred_marketplaces:
        write_marketplace(report, root, dst)
        written.append(str(dst))

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
