# Antigravity Source Adapter

Use this reference when the source is a Google Antigravity skill, rule bundle, workflow bundle, MCP config, project context folder, or agent-orchestration notes.

## Artifact Mapping

| Antigravity artifact | Target handling |
| --- | --- |
| `SKILL.md` | Usually portable after frontmatter, wording, and path cleanup. |
| `.agent/skills/<name>/SKILL.md` | Treat as an Agent Skills-compatible source. |
| `~/.gemini/antigravity/skills/<name>/SKILL.md` | Treat as a global Antigravity skill source; inspect read-only. |
| `GEMINI.md` | Treat as Antigravity/Gemini project instructions. Translate or bridge to the target project-instruction file; do not package as a skill. |
| `AGENTS.md` | Treat as cross-tool project instructions. Preserve when the target reads it, otherwise translate to the target instruction file. |
| `.agent/rules/*.md` | Treat as project or workspace rules. Convert rule intent into target instructions or dependency notes. |
| `workflows/*` or slash-invoked workflow notes | Convert intent into target trigger/workflow text when the target format is known; otherwise document as partial. |
| `mcp_config.json` or `~/.gemini/antigravity/mcp_config.json` | MCP/tool setup. Treat credentials, trust, tool filtering, and scopes as dependency-bound. |
| Agent Manager, browser subagent, artifacts, mode settings | Treat as Antigravity-specific orchestration unless the target has a known equivalent. |

## Antigravity-Specific Signals

Flag these because they require target adaptation:

- `.agent/skills/` workspace skill folders.
- `.agent/rules/` workspace rules.
- `~/.gemini/antigravity/` global Antigravity configuration.
- `mcp_config.json` MCP configuration.
- `GEMINI.md` plus optional `AGENTS.md` layering.
- Planning/Fast mode instructions.
- Agent Manager orchestration, artifacts, browser subagent behavior, and workflow invocation notes.

## Rewrite Rules

- Convert portable `.agent/skills/<name>/SKILL.md` folders directly.
- Convert `GEMINI.md`, `AGENTS.md`, and `.agent/rules/*.md` into the target's project-instruction format or a bridge note.
- Convert workflows into target command/workflow notes only when inputs, trigger, and expected output are clear.
- Keep MCP config as dependency notes unless the user explicitly asks to stage target MCP settings.
- Keep browser subagent, artifact, and Agent Manager assumptions as compatibility notes; do not claim those behaviors exist in the target.

## Classification Defaults

- Plain skills are usually portable.
- Rules and project instructions need adaptation.
- Workflows need adaptation.
- MCP config is dependency-bound.
- Agent Manager, browser subagent, artifacts, and execution-mode behavior are partial or unsupported unless explicitly mapped.
