# Codex Target Adapter

Use this reference when the target agent is Codex.

## Skill Shape

Codex skills should be staged as:

```text
<skill-name>/
  SKILL.md
  agents/openai.yaml        # optional UI metadata
  references/               # optional docs loaded on demand
  scripts/                  # optional deterministic helpers
  assets/                   # optional templates or static assets
```

`SKILL.md` frontmatter must include:

```yaml
---
name: lowercase-hyphen-name
description: Clear trigger-oriented description
---
```

Keep `SKILL.md` concise. Move long examples, source mappings, provider docs, and domain tables into `references/`.

## Project Instructions

Project guidance belongs in `AGENTS.md` or target project-instruction files, not in a skill unless it is a reusable workflow. When a Claude source has `CLAUDE.md`, recommend a target `AGENTS.md` bridge or translated project guidance with notes for Claude-only behavior. When a Gemini source has `GEMINI.md`, translate reusable guidance into `AGENTS.md` and preserve Gemini-specific extension, hook, or policy behavior as notes.

## Staging Paths

- Single skill: `skills/codex/<skill-name>/`
- Multi-skill/plugin source: `ports/<source-name>/codex/`
- Do not write directly to `~/.codex/skills/` unless the user explicitly asks for installation.

## Claude-to-Codex Rules

- Convert `CLAUDE.md` project guidance into `AGENTS.md` guidance or a bridge note; do not treat it as a skill.
- Convert Claude slash commands into trigger descriptions, workflow sections, `references/command-map.md`, or a small router skill when the source has many commands. Preserve command argument hints as required-input parsing rules.
- Convert Claude subagent/agent prompts into Codex workflow skills when they describe a reusable procedure. Keep automatic dispatch, scoped tool isolation, and managed-agent handoff as orchestration notes unless a Codex runtime equivalent is explicitly available.
- Convert plugin manifests into metadata notes, target plugin implementation plans, or grouped skill bundles. Do not treat marketplace registration or plugin installation as migrated behavior.
- Treat MCP configs as target setup artifacts. Generate `references/codex-mcp-setup.md` with server names, endpoint types/URLs, expected auth placeholders, and source tool-name mapping. Do not claim the MCP is available unless Codex has the matching server/tool configured.
- Distinguish empty hook files from active lifecycle behavior. Empty hooks are no-op records; active hooks need `references/hook-migration.md` with event, matcher, tool, input, output, and safety mapping.
- Keep references/assets when they are target-neutral and useful.

## Codex-Native Mapping Preferences

When several Codex equivalents are possible, prefer the narrowest native surface that preserves user-facing behavior:

- Reusable task knowledge -> Codex skill.
- Project-wide guidance -> `AGENTS.md`.
- Many command entrypoints -> command map plus optional router skill.
- Named workflow agent -> workflow skill that names expected artifacts, review stops, required tools, and component skills.
- Managed subagents -> orchestration recipe or explicit subtask delegation notes; do not promise automatic spawning.
- Remote or local MCP config -> Codex MCP setup notes/config snippets with disabled/manual credential placeholders.
- Office/document/spreadsheet/presentation MCP references -> Codex Documents, Spreadsheets, Presentations, connector, or file-artifact workflow notes when those target capabilities are available.
- Empty hook config -> no-op compatibility note.
- Active hook config -> partial migration plan or unsupported item until the target hook mechanism is known.

## Gemini-to-Codex Rules

- Convert `GEMINI.md` project guidance into `AGENTS.md`; do not treat it as a skill.
- Convert `gemini-extension.json` into a Codex plugin implementation plan or `.codex-plugin/plugin.json` only when fields are known.
- Convert Gemini `commands/*.toml` into workflow sections or Codex command notes.
- Convert Gemini subagent Markdown into `.codex/agents/*.toml` only for known fields.
- Treat Gemini policies and hooks as unsupported until Codex hook or policy equivalents are explicitly mapped.

## Audit Recommendations

In audit-only mode, recommend the concrete Codex staging layout and automatic port work without creating files:

- Skills: `ports/<source-name>/codex/skills/<skill-name>/SKILL.md` for plugin ecosystems.
- Commands: `ports/<source-name>/codex/references/command-map.md` and, for many commands, `ports/<source-name>/codex/skills/<source-name>-command-router/SKILL.md`.
- Agent workflows: `ports/<source-name>/codex/skills/<agent-name>-workflow/SKILL.md` plus orchestration references when needed.
- MCP setup: `ports/<source-name>/codex/references/codex-mcp-setup.md`.
- Dependencies: `ports/<source-name>/codex/references/dependencies.md` for subscriptions, app provisioning, provider accounts, and credentials.
- Hooks: `ports/<source-name>/codex/references/hooks.md` for no-op hooks or `references/hook-migration.md` for active hooks.
- Unsupported behavior: `ports/<source-name>/codex/references/unsupported.md`.

Only list credentials, subscriptions, MCP enablement, app provisioning, final install, and regulated human review as remaining manual steps.

## Validation

Run the Codex skill validator when available:

```bash
python3 /Users/yanivd/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>
```

For index readiness, also run discovery checks when available:

```bash
npx skills add . --list
```

Ask the user before running commands likely to produce large output.
