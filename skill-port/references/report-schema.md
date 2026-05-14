# Report Schema

Every audit or port should produce deterministic JSON and a human-readable Markdown summary.

## JSON Fields

```json
{
  "schema_version": "1.0",
  "mode": "audit-only",
  "target_agent": "codex",
  "source": {
    "path": "/absolute/source/path",
    "name": "source-name",
    "type": "skill|plugin|repo|command-bundle|agent-bundle|mcp-backed-plugin|unknown"
  },
  "locations": {
    "source_read_from": "/absolute/source/path",
    "output_path": null,
    "installed": false
  },
  "compatibility": {
    "status": "portable|needs-adaptation|dependency-bound|unsupported",
    "reasons": []
  },
  "inventory": {
    "files_total": 0,
    "skill_files": [],
    "command_files": [],
    "agent_files": [],
    "mcp_files": [],
    "manifest_files": [],
    "script_files": [],
    "asset_files": []
  },
  "security": {
    "risk_level": "low|medium|high",
    "findings": []
  },
  "porting_map": [],
  "manual_steps": []
}
```

## Markdown Summary

Keep the Markdown report concise:

1. Source and target.
2. Compatibility status.
3. Security risk level and findings.
4. Porting map.
5. Manual setup steps.
6. Install command if files were staged.

## Status Meanings

- `portable`: can be used with minimal wording/path changes.
- `needs-adaptation`: useful content exists, but target-specific syntax or behavior must be rewritten.
- `dependency-bound`: core behavior depends on MCPs, APIs, app connectors, credentials, or subscriptions.
- `unsupported`: source behavior is mostly unavailable in the target without new tooling.
