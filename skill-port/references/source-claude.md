# Claude Source Adapter

Use this reference when the source is a Claude Code skill, Claude Code plugin, Claude Cowork plugin, slash command bundle, agent bundle, hook config, MCP-backed plugin, or Claude Managed Agent cookbook.

## Artifact Mapping

| Claude artifact | Target handling |
| --- | --- |
| `SKILL.md` | Usually portable after frontmatter, wording, and path cleanup. |
| `.claude/skills/<name>/SKILL.md` | Port to `skills/<target-agent>/<name>/SKILL.md` for a single skill. |
| `plugins/**/skills/<name>/SKILL.md` | Port each portable skill or split into target-agent staged folders. |
| `.claude/commands/*.md` or `commands/*.md` | Convert command intent into trigger text, workflow sections, or prompt snippets. Do not claim native slash-command support unless the target has it. |
| `.claude/agents/*.md` or `agents/*.md` | Convert procedural parts into skills. Keep role/runtime/subagent behavior as target-specific notes unless supported. |
| `.claude/settings*.json` hooks | Treat as unsupported lifecycle behavior unless the target has an equivalent hook mechanism. |
| `.claude-plugin/`, `plugin.json`, `manifest.json` | Inventory metadata. Convert plugin behavior into skills plus dependency notes. |
| `.mcp.json` or MCP server configs | Treat as dependency-bound. Capture server names, URLs, auth requirements, and credentials needed. |
| Managed Agent `agent.yaml` and callable agents | Treat as orchestration behavior. Port reusable instructions only; report subagent handoff requirements. |
| Cowork dispatch/project behavior | Treat as Claude/Cowork-specific unless the target environment provides a matching workflow. |

## Rewrite Rules

- Replace "Claude" wording with target-neutral wording unless the behavior is actually Claude-specific.
- Preserve domain expertise, examples, templates, and quality checks.
- Preserve safety disclaimers and human-review requirements.
- Convert `$ARGUMENTS` into explicit instruction parsing or a short user question.
- Remove assumptions about `.claude` paths from reusable instructions.
- Keep MCP/provider access as dependency notes, not as installed capabilities.

## Classification Defaults

- Plain markdown workflows are usually portable.
- Scripts are portable only after security review and dependency inventory.
- Slash commands need adaptation.
- Hooks, auto-install behavior, Cowork dispatch, and Managed Agent subagent routing are not portable by default.
