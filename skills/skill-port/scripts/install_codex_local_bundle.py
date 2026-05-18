#!/usr/bin/env python3
"""Install a staged Codex marketplace as a local Codex plugin bundle.

This follows Codex's private local bundle pattern:
- register marketplace with `codex plugin marketplace add`
- copy each plugin into ~/.codex/plugins/cache/<marketplace>/<plugin>/<version>
- set [features] plugins = true
- set [plugins."<plugin>@<marketplace>"] enabled = true

It does not execute source scripts, package managers, hooks, MCP servers, or plugin commands.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install a staged Codex marketplace as a local plugin bundle.")
    parser.add_argument("marketplace", help="Path to staged codex-marketplace directory")
    parser.add_argument("--codex-home", default=str(Path.home() / ".codex"), help="Codex home directory")
    parser.add_argument("--codex-bin", default="codex", help="Codex CLI binary")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return value


def set_table_key(lines: list[str], *, header: str, key: str, value: str) -> list[str]:
    out: list[str] = []
    inside_target = False
    seen_target = False
    target_has_key = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if inside_target and not target_has_key:
                out.append(f"{key} = {value}")
            inside_target = stripped == header
            if inside_target:
                seen_target = True
                target_has_key = False
        is_target_key = False
        if inside_target and "=" in stripped:
            is_target_key = stripped.split("=", 1)[0].strip() == key
        if is_target_key:
            out.append(f"{key} = {value}")
            target_has_key = True
        else:
            out.append(line)
    if inside_target and not target_has_key:
        out.append(f"{key} = {value}")
    if not seen_target:
        if out and out[-1] != "":
            out.append("")
        out.extend([header, f"{key} = {value}"])
    return out


def main() -> int:
    args = parse_args()
    marketplace_root = Path(args.marketplace).resolve()
    codex_home = Path(args.codex_home).resolve()
    marketplace_file = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace_file.exists():
        raise SystemExit(f"Missing marketplace file: {marketplace_file}")
    marketplace = load_json(marketplace_file)
    marketplace_name = marketplace.get("name")
    if not isinstance(marketplace_name, str) or not marketplace_name:
        raise SystemExit(f"Marketplace name is required: {marketplace_file}")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        raise SystemExit(f"Marketplace plugins must be a list: {marketplace_file}")

    subprocess.run([args.codex_bin, "plugin", "marketplace", "add", str(marketplace_root)], check=True)

    enabled: list[str] = []
    for entry in plugins:
        if not isinstance(entry, dict):
            raise SystemExit(f"Invalid marketplace entry: {entry!r}")
        plugin_name = entry.get("name")
        source = entry.get("source") or {}
        source_path = source.get("path")
        if not isinstance(plugin_name, str) or not plugin_name:
            raise SystemExit(f"Invalid plugin name in entry: {entry!r}")
        if source.get("source") != "local" or not isinstance(source_path, str) or not source_path.startswith("./"):
            raise SystemExit(f"Unsupported source for {plugin_name}: {source!r}")
        plugin_source = marketplace_root / source_path[2:]
        manifest_file = plugin_source / ".codex-plugin" / "plugin.json"
        manifest = load_json(manifest_file)
        if manifest.get("name") != plugin_name:
            raise SystemExit(f"Manifest name mismatch for {plugin_name}: {manifest.get('name')!r}")
        version = str(manifest.get("version") or "0.1.0")
        cache_dir = codex_home / "plugins" / "cache" / marketplace_name / plugin_name / version
        shutil.rmtree(cache_dir, ignore_errors=True)
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(plugin_source, cache_dir)
        enabled.append(f"{plugin_name}@{marketplace_name}")

    config_path = codex_home / "config.toml"
    lines = config_path.read_text(encoding="utf-8").splitlines() if config_path.exists() else []
    lines = set_table_key(lines, header="[features]", key="plugins", value="true")
    for plugin_key in enabled:
        lines = set_table_key(lines, header=f'[plugins."{plugin_key}"]', key="enabled", value="true")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(json.dumps({"marketplace": marketplace_name, "enabled": enabled}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
