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

## Staging Paths

- Single skill: `skills/codex/<skill-name>/`
- Multi-skill/plugin source: `ports/<source-name>/codex/`
- Do not write directly to `~/.codex/skills/` unless the user explicitly asks for installation.

## Claude-to-Codex Rules

- Convert Claude slash commands into trigger descriptions or workflow sections.
- Convert Claude subagent/agent prompts only when they are procedural instructions; otherwise report them as orchestration requirements.
- Convert plugin manifests into dependency notes or a plugin implementation plan.
- Treat MCP configs as required setup. Do not claim the MCP is available unless Codex has the matching tool configured.
- Keep references/assets when they are target-neutral and useful.

## Audit Recommendations

In audit-only mode, recommend the concrete Codex staging layout and automatic port work without creating files:

- Skills: `ports/<source-name>/codex/skills/<skill-name>/SKILL.md` for plugin ecosystems.
- Commands: `ports/<source-name>/codex/references/commands.md`.
- Dependencies: `ports/<source-name>/codex/references/dependencies.md`.
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
