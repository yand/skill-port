# Antigravity Target Adapter

Use this reference when the target agent is Google Antigravity.

## Skill Shape

Antigravity skills should be staged as:

```text
<skill-name>/
  SKILL.md
  references/        # optional docs loaded on demand
  scripts/           # optional helpers, only after security review
  assets/            # optional templates or static assets
```

Antigravity can use workspace skills under `.agent/skills/<skill-folder>/` and global skills under `~/.gemini/antigravity/skills/<skill-folder>/`. During porting, stage files under this repository first; installation is a separate step.

## Project Instructions

Antigravity uses `GEMINI.md` for Antigravity-specific project guidance and can also consume `AGENTS.md` in newer versions for cross-tool rules. Use `GEMINI.md` for Antigravity-only behavior and preserve `AGENTS.md` when the source is intended to stay cross-tool.

Rules under `.agent/rules/` should be treated as workspace rules, not reusable skills, unless the source clearly describes a reusable workflow.

## Staging Paths

- Single skill: `skills/antigravity/<skill-name>/`
- Multi-skill/plugin source: `ports/<source-name>/antigravity/`
- Do not write directly to `.agent/skills/`, `.agent/rules/`, `~/.gemini/antigravity/skills/`, or `~/.gemini/antigravity/mcp_config.json` unless the user explicitly asks for installation.

## Target-Specific Package Surfaces

| Target artifact | Use |
| --- | --- |
| `.agent/skills/<name>/SKILL.md` | Workspace skill install location. |
| `~/.gemini/antigravity/skills/<name>/SKILL.md` | Global skill install location. |
| `GEMINI.md` | Antigravity-specific project instructions. |
| `AGENTS.md` | Cross-tool project instructions. |
| `.agent/rules/*.md` | Workspace rules. |
| `mcp_config.json` | Antigravity MCP setup; keep dependency-bound unless explicitly requested. |
| Workflow notes | Slash-invoked workflows; convert only when trigger and schema are clear. |

## Porting Rules

- Convert Agent Skills-compatible `SKILL.md` files directly after frontmatter and wording cleanup.
- Convert Claude `CLAUDE.md` and Codex `AGENTS.md` into `GEMINI.md` when the guidance is Antigravity-specific; preserve `AGENTS.md` when cross-tool behavior is intended.
- Convert Claude slash commands, Codex command-like workflows, and Gemini commands into workflow notes unless an Antigravity workflow schema is known.
- Keep MCP/provider setup as dependency notes unless the user explicitly asks to stage `mcp_config.json`.
- Treat browser subagent behavior, artifacts, execution modes, and Agent Manager orchestration as Antigravity-specific notes rather than portable skill behavior.

## Validation

When Antigravity is available, validate by installing into a temporary workspace-level `.agent/skills/<name>/` path and confirming the skill appears in the IDE. Avoid global install until the user approves.
