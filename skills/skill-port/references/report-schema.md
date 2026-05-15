# Report Schema

Every audit or port should produce deterministic JSON and a human-readable Markdown summary.

## JSON Fields

```json
{
  "schema_version": "1.2",
  "mode": "audit-only",
  "target_agent": "codex",
  "source": {
    "path": "/absolute/source/path",
    "name": "source-name",
    "type": "skill|plugin|extension|repo|command-bundle|agent-bundle|mcp-backed-plugin|mcp-backed-extension|unknown",
    "detected_ecosystems": ["agent-skills", "claude", "codex", "gemini", "antigravity"]
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
  "recommendation": {
    "target_agent_inferred": true,
    "recommended_scope": "focused|whole-ecosystem|single-skill|unknown",
    "recommended_scope_reason": "",
    "proposed_target_layout": "ports/source-name/codex/",
    "next_port_command": "Use skill-port in port mode..."
  },
  "inventory": {
    "files_total": 0,
    "instruction_files": [],
    "skill_files": [],
    "command_files": [],
    "agent_files": [],
    "mcp_files": [],
    "manifest_files": [],
    "hook_files": [],
    "script_files": [],
    "asset_files": []
  },
  "layer_summary": {
    "project_instructions": 0,
    "skills": 0,
    "commands": 0,
    "agents": 0,
    "plugins": 0,
    "mcp_tools": 0,
    "hooks": 0
  },
  "layer_details": {
    "empty_hook_files": [],
    "active_hook_files": []
  },
  "conversion_status": {
    "direct": 0,
    "translated": 0,
    "partial": 0,
    "unsupported": 0,
    "manual": 0
  },
  "security": {
    "risk_level": "low|medium|high",
    "findings": []
  },
  "porting_map": [],
  "auto_port_candidates": [],
  "auto_adaptation_candidates": [],
  "dependency_bound_items": [],
  "unsupported_items": [],
  "remaining_manual_steps": []
}
```

## Markdown Summary

Keep the Markdown report concise:

1. Source and target.
2. Compatibility status.
3. Security risk level and findings.
4. Recommended scope and proposed target layout.
5. Automatic work available in port mode.
6. Command, agent/workflow, MCP, and hook migration plans when those layers exist.
7. Remaining manual setup steps.
8. Install command if files were staged.

## Status Meanings

- `portable`: can be used with minimal wording/path changes.
- `needs-adaptation`: useful content exists, but target-specific syntax or behavior must be rewritten.
- `dependency-bound`: core behavior depends on MCPs, APIs, app connectors, credentials, or subscriptions.
- `unsupported`: source behavior is mostly unavailable in the target without new tooling.

## Ecosystem Detection

`detected_ecosystems` is informational. It should be derived from stable file paths and source-specific markers:

- `agent-skills`: `SKILL.md` files.
- `claude`: `.claude/`, `.claude-plugin/`, `CLAUDE.md`, Claude-specific fields or commands.
- `codex`: `.codex/`, `.codex-plugin/`, `.agents/plugins/`, `AGENTS.md`, `agents/openai.yaml`.
- `gemini`: `.gemini/`, `GEMINI.md`, `gemini-extension.json`, Gemini command/hook/policy markers.
- `antigravity`: `.agent/skills/`, `.agent/rules/`, `~/.gemini/antigravity/`, `mcp_config.json`, Antigravity rule/workflow/orchestration markers.

## Audit Mode Standard

Audit mode is read-only, but it should still be decisive. Prefer `remaining_manual_steps` only for irreducibly manual work: credentials, subscriptions, MCP enablement, app provisioning, final install, and regulated human review. Put rewrite, layout, scope, and dependency documentation work into recommendations or auto-candidate fields.

## Layer Mapping Standard

Reports should avoid treating every non-skill source artifact as simply unsupported:

- Commands should map to target entrypoints, command maps, or router skills.
- Agent prompts should map to workflow skills, target agent definitions, or orchestration recipes.
- MCP configs should map to target setup notes/config snippets plus manual credential/enablement steps.
- Empty hook configs should appear in `layer_details.empty_hook_files` and should not by themselves make compatibility `unsupported`.
- Active hook configs should appear in `layer_details.active_hook_files` and should be `partial` or `unsupported` until the target lifecycle equivalent is known.
