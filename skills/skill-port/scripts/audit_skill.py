#!/usr/bin/env python3
"""Read-only deterministic auditor for agent skills and plugin folders."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
MAX_TEXT_BYTES = 1_000_000

SCRIPT_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".rb",
    ".pl",
    ".php",
}

ASSET_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".pdf",
    ".pptx",
    ".docx",
    ".xlsx",
    ".csv",
    ".zip",
}

def lit(*parts: str) -> str:
    return "".join(parts)


PATTERNS = {
    "secret_like": [
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
    ],
    "destructive_command": [
        re.compile(r"\brm\s+-rf\b"),
        re.compile(r"\bgit\s+reset\s+--hard\b"),
        re.compile(r"\bchmod\s+-R\s+777\b"),
        re.compile(r"\bdd\s+if=.*\bof="),
        re.compile(r"\bmkfs(?:\.[a-z0-9]+)?\b"),
    ],
    "shell_execution": [
        re.compile(r"\bsubprocess\.(?:run|Popen|call|check_call|check_output)\b"),
        re.compile(r"\bos\.system\b"),
        re.compile(r"\bchild_process\b"),
        re.compile(r"\beval\s*\("),
        re.compile(r"\bexec\s*\("),
    ],
    "network_call": [
        re.compile(r"https?://[^\s)'\"<>]+"),
        re.compile(r"\b(?:curl|wget)\s+"),
        re.compile(r"\bfetch\s*\("),
        re.compile(r"\brequests\.(?:get|post|put|delete|patch)\b"),
        re.compile(r"\baxios\.(?:get|post|put|delete|patch)\b"),
    ],
    "install_hook": [
        re.compile(rf'"{lit("post", "install")}"\s*:'),
        re.compile(rf'"{lit("pre", "install")}"\s*:'),
        re.compile(rf"\b{lit('post', 'install')}\b"),
    ],
    "credential_access": [
        re.compile(rf"\.{lit('s', 's', 'h')}/"),
        re.compile(rf"\.{lit('a', 'w', 's')}/"),
        re.compile(rf"\.{lit('c', 'o', 'n', 'f', 'i', 'g')}/"),
        re.compile(r"\bkeychain\b", re.IGNORECASE),
        re.compile(r"\bprintenv\b"),
        re.compile(r"\benv\s*>\b"),
    ],
    "claude_specific": [
        re.compile(r"\.claude(?:/|\\)"),
        re.compile(r"\bClaude Code\b"),
        re.compile(r"\bCowork\b"),
        re.compile(r"\$" + lit("ARG", "UMENTS")),
        re.compile(r"\bclaude\s+plugin\b"),
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit an agent skill/plugin folder without executing it.")
    parser.add_argument("source", help="Path to a skill, plugin, or repository folder")
    parser.add_argument("--target-agent", default="codex", help="Target agent name for compatibility mapping")
    parser.add_argument("--mode", default="audit-only", choices=["audit-only", "port", "case-study"])
    parser.add_argument("--format", default="json", choices=["json", "markdown"], help="Output format")
    parser.add_argument("--output", help="Optional output file. Without this, report is printed to stdout.")
    return parser.parse_args()


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_hidden(rel: str) -> bool:
    return any(part.startswith(".") for part in rel.split("/"))


def is_binary(data: bytes) -> bool:
    if b"\x00" in data:
        return True
    sample = data[:4096]
    if not sample:
        return False
    non_text = sum(1 for byte in sample if byte < 9 or (13 < byte < 32))
    return non_text / len(sample) > 0.30


def read_text_sample(path: Path) -> tuple[str, bool]:
    data = path.read_bytes()[:MAX_TEXT_BYTES]
    binary = is_binary(data)
    if binary:
        return "", True
    return data.decode("utf-8", errors="replace"), False


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    raw = text[4:end].splitlines()
    data: dict[str, str] = {}
    current_key = ""
    block: list[str] = []
    for line in raw:
        if block and (line.startswith(" ") or line.strip() == ""):
            block.append(line.strip())
            continue
        if block and current_key:
            data[current_key] = "\n".join(block).strip()
            block = []
            current_key = ""
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if value in {"|", ">"}:
            current_key = key
            block = []
        else:
            data[key] = value
    if block and current_key:
        data[current_key] = "\n".join(block).strip()
    return data


def file_kind(path: Path, rel: str) -> str:
    name = path.name
    suffix = path.suffix.lower()
    parts = rel.split("/")
    if rel == "agents/openai.yaml":
        return "metadata"
    if name == "SKILL.md":
        return "skill"
    if name in {".mcp.json", "mcp.json"} or "mcp" in name.lower():
        return "mcp"
    if name in {"plugin.json", "manifest.json"} or ".claude-plugin" in parts:
        return "manifest"
    if "commands" in parts and suffix in {".md", ".txt"}:
        return "command"
    if "agents" in parts and suffix in {".md", ".yaml", ".yml", ".json"}:
        return "agent"
    if suffix in SCRIPT_SUFFIXES or "scripts" in parts:
        return "script"
    if suffix in ASSET_SUFFIXES or "assets" in parts or "examples" in parts:
        return "asset"
    return "file"


def scan_patterns(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for category, patterns in PATTERNS.items():
        matches: set[str] = set()
        for pattern in patterns:
            for match in pattern.finditer(text):
                value = match.group(0)
                if category == "network_call" and value.startswith("http://www.w3.org/"):
                    continue
                if category == "secret_like":
                    value = redact(value)
                matches.add(value[:160])
        if matches:
            findings.append({"category": category, "matches": sorted(matches)})
    return findings


def redact(value: str) -> str:
    if len(value) <= 12:
        return "<redacted>"
    return f"{value[:6]}...{value[-4:]}"


def classify_source(inventory: dict[str, list[str]], has_claude_plugin_dir: bool) -> str:
    has_skills = bool(inventory["skill_files"])
    has_commands = bool(inventory["command_files"])
    has_agents = bool(inventory["agent_files"])
    has_mcp = bool(inventory["mcp_files"])
    has_manifest = bool(inventory["manifest_files"]) or has_claude_plugin_dir

    if has_manifest and has_mcp:
        return "mcp-backed-plugin"
    if has_manifest:
        return "plugin"
    if has_skills and (has_commands or has_agents or has_mcp):
        return "plugin"
    if has_skills:
        return "skill"
    if has_commands:
        return "command-bundle"
    if has_agents:
        return "agent-bundle"
    return "unknown"


def compatibility_status(inventory: dict[str, list[str]], security_findings: list[dict[str, Any]]) -> dict[str, Any]:
    reasons: list[str] = []
    categories = {finding["category"] for finding in security_findings}
    if inventory["mcp_files"]:
        reasons.append("MCP configuration requires target-agent setup and credentials.")
    if inventory["command_files"]:
        reasons.append("Slash commands or command files must be rewritten as target-agent workflows.")
    if inventory["agent_files"]:
        reasons.append("Agent/subagent files may describe orchestration that is not directly portable.")
    if "claude_specific" in categories:
        reasons.append("Claude-specific paths, commands, or runtime wording need adaptation.")
    if {"secret_like", "destructive_command", "credential_access", "install_hook"} & categories:
        reasons.append("Security findings require review before installation or porting.")

    if {"secret_like", "destructive_command", "credential_access", "install_hook"} & categories:
        status = "unsupported"
    elif inventory["mcp_files"]:
        status = "dependency-bound"
    elif inventory["command_files"] or inventory["agent_files"] or "claude_specific" in categories:
        status = "needs-adaptation"
    elif inventory["skill_files"]:
        status = "portable"
    else:
        status = "needs-adaptation"
        reasons.append("No standard SKILL.md files were found.")

    return {"status": status, "reasons": sorted(set(reasons))}


def risk_level(security_findings: list[dict[str, Any]], file_records: list[dict[str, Any]]) -> str:
    categories = {finding["category"] for finding in security_findings}
    if {"secret_like", "destructive_command", "credential_access", "install_hook"} & categories:
        return "high"
    if {"shell_execution", "network_call"} & categories:
        return "medium"
    if any(record["kind"] in {"script", "mcp"} or record["binary"] for record in file_records):
        return "medium"
    return "low"


def target_name_from_skill(path: str, frontmatter_by_file: dict[str, dict[str, str]]) -> str:
    frontmatter = frontmatter_by_file.get(path, {})
    name = frontmatter.get("name", "").strip()
    if name:
        return re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-") or "ported-skill"
    parent = Path(path).parent.name if Path(path).parent.name else Path(path).stem
    return re.sub(r"[^a-z0-9-]+", "-", parent.lower()).strip("-") or "ported-skill"


def build_porting_map(root: Path, inventory: dict[str, list[str]], frontmatter_by_file: dict[str, dict[str, str]], target_agent: str) -> list[dict[str, str]]:
    source_name = re.sub(r"[^a-z0-9-]+", "-", root.name.lower()).strip("-") or "source"
    multi = len(inventory["skill_files"]) > 1 or bool(inventory["manifest_files"] or inventory["command_files"] or inventory["agent_files"])
    mapped: list[dict[str, str]] = []

    for skill_file in inventory["skill_files"]:
        skill_name = target_name_from_skill(skill_file, frontmatter_by_file)
        if multi:
            target = f"ports/{source_name}/{target_agent}/skills/{skill_name}/SKILL.md"
        else:
            target = f"skills/{target_agent}/{skill_name}/SKILL.md"
        mapped.append({"source": skill_file, "target": target, "action": "port-skill"})

    for command_file in inventory["command_files"]:
        mapped.append({"source": command_file, "target": f"ports/{source_name}/{target_agent}/references/commands.md", "action": "adapt-command"})

    for agent_file in inventory["agent_files"]:
        mapped.append({"source": agent_file, "target": f"ports/{source_name}/{target_agent}/references/agents.md", "action": "document-orchestration"})

    for mcp_file in inventory["mcp_files"]:
        mapped.append({"source": mcp_file, "target": f"ports/{source_name}/{target_agent}/references/dependencies.md", "action": "document-dependency"})

    return mapped


def manual_steps(report: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    if report["inventory"]["mcp_files"]:
        steps.append("Configure equivalent MCP servers, credentials, and provider subscriptions for the target agent.")
    if report["inventory"]["command_files"]:
        steps.append("Review command mappings and rewrite slash-command behavior as target-agent triggers or workflows.")
    if report["inventory"]["agent_files"]:
        steps.append("Review agent/subagent orchestration and decide whether to port as skills, custom agents, or documentation.")
    if report["security"]["risk_level"] != "low":
        steps.append("Review security findings before installing or running any source scripts.")
    if report["porting_map"]:
        first_target = report["porting_map"][0]["target"]
        steps.append(f"After staging files, validate the target skill and install with the target agent's normal installer, e.g. npx skills add . --agent {report['target_agent']}.")
    return steps


def audit(root: Path, target_agent: str, mode: str) -> dict[str, Any]:
    root = root.resolve()
    if not root.exists():
        raise SystemExit(f"Source path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Source path must be a directory: {root}")

    inventory = {
        "skill_files": [],
        "command_files": [],
        "agent_files": [],
        "mcp_files": [],
        "manifest_files": [],
        "script_files": [],
        "asset_files": [],
    }
    file_records: list[dict[str, Any]] = []
    security_findings: list[dict[str, Any]] = []
    frontmatter_by_file: dict[str, dict[str, str]] = {}
    has_claude_plugin_dir = False

    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if path.is_dir():
            if path.name == ".claude-plugin":
                has_claude_plugin_dir = True
            continue
        rel = relpath(path, root)
        if rel.startswith(".git/"):
            continue
        kind = file_kind(path, rel)
        try:
            size = path.stat().st_size
            text, binary = read_text_sample(path)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except FileNotFoundError:
            continue
        record = {
            "path": rel,
            "kind": kind,
            "size_bytes": size,
            "sha256": digest,
            "hidden": is_hidden(rel),
            "binary": binary,
        }
        file_records.append(record)

        key = f"{kind}_files"
        if key in inventory:
            inventory[key].append(rel)

        if kind == "skill" and text:
            frontmatter_by_file[rel] = parse_frontmatter(text)

        if text:
            for finding in scan_patterns(text):
                security_findings.append({"file": rel, **finding})
        elif binary and (kind not in {"asset"} or size > 5_000_000):
            security_findings.append({"file": rel, "category": "binary_or_large_file", "matches": [f"{size} bytes"]})

    source_type = classify_source(inventory, has_claude_plugin_dir)
    compatibility = compatibility_status(inventory, security_findings)
    porting = build_porting_map(root, inventory, frontmatter_by_file, target_agent)

    source_name = re.sub(r"[^a-z0-9-]+", "-", root.name.lower()).strip("-") or "source"
    output_path = None
    if mode == "port":
        output_path = f"ports/{source_name}/{target_agent}/" if source_type != "skill" or len(inventory["skill_files"]) > 1 else None
        if output_path is None and porting:
            output_path = str(Path(porting[0]["target"]).parent)

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "target_agent": target_agent,
        "source": {
            "path": str(root),
            "name": source_name,
            "type": source_type,
        },
        "locations": {
            "source_read_from": str(root),
            "output_path": output_path,
            "installed": False,
        },
        "compatibility": compatibility,
        "inventory": {
            "files_total": len(file_records),
            **{key: sorted(value) for key, value in inventory.items()},
            "files": file_records,
        },
        "security": {
            "risk_level": risk_level(security_findings, file_records),
            "findings": sorted(security_findings, key=lambda item: (item["file"], item["category"])),
        },
        "porting_map": porting,
        "manual_steps": [],
    }
    report["manual_steps"] = manual_steps(report)
    return report


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Skill Port Audit: {report['source']['name']}",
        "",
        f"- Source: `{report['source']['path']}`",
        f"- Source type: `{report['source']['type']}`",
        f"- Target agent: `{report['target_agent']}`",
        f"- Mode: `{report['mode']}`",
        f"- Compatibility: `{report['compatibility']['status']}`",
        f"- Security risk: `{report['security']['risk_level']}`",
        f"- Installed: `{str(report['locations']['installed']).lower()}`",
    ]
    if report["locations"]["output_path"]:
        lines.append(f"- Output path: `{report['locations']['output_path']}`")

    if report["compatibility"]["reasons"]:
        lines.extend(["", "## Compatibility Reasons"])
        lines.extend(f"- {reason}" for reason in report["compatibility"]["reasons"])

    lines.extend(["", "## Inventory"])
    for key in ["skill_files", "command_files", "agent_files", "mcp_files", "manifest_files", "script_files", "asset_files"]:
        lines.append(f"- {key}: {len(report['inventory'][key])}")

    if report["security"]["findings"]:
        lines.extend(["", "## Security Findings"])
        for finding in report["security"]["findings"]:
            lines.append(f"- `{finding['file']}`: {finding['category']} ({len(finding['matches'])} match(es))")

    if report["porting_map"]:
        lines.extend(["", "## Porting Map"])
        for item in report["porting_map"]:
            lines.append(f"- `{item['source']}` -> `{item['target']}` ({item['action']})")

    if report["manual_steps"]:
        lines.extend(["", "## Manual Steps"])
        lines.extend(f"- {step}" for step in report["manual_steps"])

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    report = audit(Path(args.source), args.target_agent, args.mode)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.format == "json" else to_markdown(report)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
