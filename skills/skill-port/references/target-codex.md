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
- Plugin or marketplace source: `ports/<source-name>/codex-marketplace/`
- Multi-skill non-plugin source: `ports/<source-name>/codex/`
- Do not write directly to `~/.codex/skills/` unless the user explicitly asks for installation.

## Plugin Shape

Codex plugins bundle skills, app integrations, MCP servers, hooks, and assets behind one installable unit. Prefer a Codex plugin target whenever the source is a Claude/Cowork plugin, MCP-backed plugin, plugin marketplace, or multi-plugin repository.

Stage plugin sources as a repo-style marketplace so they can be exposed with `codex plugin marketplace add` and installed through Codex:

```text
ports/<source-name>/codex-marketplace/
  .agents/plugins/marketplace.json
  plugins/<plugin-name>/
    .codex-plugin/plugin.json
    skills/
    .mcp.json
    hooks/hooks.json
    references/
```

Codex plugin manifests use `.codex-plugin/plugin.json` as the required entry point. Manifest fields such as `skills`, `mcpServers`, `apps`, and `hooks` should point to plugin-root-relative paths such as `./skills/`, `./.mcp.json`, `./.app.json`, and `./hooks/hooks.json`. The manifest `name` must match the marketplace plugin `name`; prefer the staged plugin folder slug as the Codex plugin identifier and preserve the source display name in `interface.displayName` or descriptive fields.

Include an `interface` object for plugin-directory visibility and install-surface copy. At minimum, generate `displayName`, `shortDescription`, `longDescription`, `developerName`, `category`, `capabilities`, and a simple `defaultPrompt`. Missing interface metadata can make otherwise valid local plugins hard to discover in Codex Desktop.

Codex marketplace files live at `$REPO_ROOT/.agents/plugins/marketplace.json` for repo-scoped marketplaces or `~/.agents/plugins/marketplace.json` for a personal marketplace. Marketplace entries must include `source`, `policy`, and `category`. Local `source.path` values must start with `./` and resolve inside the marketplace root. For staged ports, prefer a repo-style marketplace root at `ports/<source-name>/codex-marketplace/` and expose it with:

```bash
codex plugin marketplace add <absolute-path-to-codex-marketplace>
```

After adding or changing a marketplace, stop and tell the user to restart Codex. The plugin directory should then show the marketplace; install and enable the desired plugins there or through another official Codex UI/command when available. Do not edit `~/.codex/config.toml` by hand to force `[plugins."<name>@<marketplace>"] enabled = true` entries. Do not describe copied folders, marketplace registration, or hand-edited config as "installed."

For Codex Desktop local testing, use Codex's private local bundle pattern when the user explicitly asks to install staged plugins:

```bash
python3 scripts/install_codex_local_bundle.py <staged-codex-marketplace>
```

This registers the staged marketplace, copies each plugin into `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>`, sets `[features] plugins = true`, and enables `[plugins."<plugin>@<marketplace>"] enabled = true`. It does not execute source scripts, package managers, hooks, MCP servers, or plugin commands. The user must restart Codex before testing.

## Claude-to-Codex Rules

- Convert `CLAUDE.md` project guidance into `AGENTS.md` guidance or a bridge note; do not treat it as a skill.
- Convert Claude plugin manifests into `.codex-plugin/plugin.json`, not only notes. Preserve version/description/author where possible, but keep the Codex manifest `name` aligned with the marketplace entry and staged plugin folder. Add `skills`, `mcpServers`, `hooks`, and install-surface `interface` metadata.
- Preserve original creator/author metadata as source attribution. Do not replace a source creator with the porter. If a single command file is ported without its surrounding plugin manifest, preserve any command-frontmatter creator/author fields and document missing source metadata rather than inventing ownership.
- Convert Claude marketplace manifests into Codex-valid `.agents/plugins/marketplace.json` entries with `source`, `policy`, and `category` fields that point at staged Codex plugin directories.
- Convert Claude slash commands into bundled plugin skills, trigger descriptions, workflow sections, and `references/command-map.md`. Preserve command names, aliases, descriptions, argument hints, and required-input parsing rules.
- Convert Claude subagent/agent prompts into bundled Codex workflow skills when they describe a reusable procedure. Keep automatic dispatch, scoped tool isolation, and managed-agent handoff as orchestration notes unless a Codex runtime equivalent is explicitly available.
- Treat MCP configs as bundled plugin MCP artifacts. Generate plugin `.mcp.json` plus `references/mcp-setup.md` with server names, endpoint types/URLs, expected auth placeholders, source tool-name mapping, provider accounts, and subscription requirements. Do not claim the MCP is usable until credentials/tool enablement are configured.
- Distinguish empty hook files from active lifecycle behavior. Empty hooks can be copied as no-op `hooks/hooks.json`; active hooks may target `hooks/hooks.json` only when schema and safety are understood, otherwise create `references/hook-migration.md` with event, matcher, tool, input, output, and safety mapping.
- Keep references/assets when they are target-neutral and useful.

## Codex-Native Mapping Preferences

When several Codex equivalents are possible, prefer the narrowest native surface that preserves user-facing behavior:

- Claude plugin or marketplace -> Codex plugin or Codex marketplace.
- Reusable task knowledge inside a plugin -> bundled Codex plugin skill.
- Project-wide guidance -> `AGENTS.md`.
- Many command entrypoints -> plugin `references/command-map.md` plus bundled command-router skill.
- Named workflow agent -> bundled workflow skill that names expected artifacts, review stops, required tools, and component skills.
- Managed subagents -> orchestration recipe or explicit subtask delegation notes; do not promise automatic spawning.
- Remote or local MCP config -> plugin `.mcp.json` plus setup notes/config snippets with disabled/manual credential placeholders.
- Office/document/spreadsheet/presentation MCP references -> Codex Documents, Spreadsheets, Presentations, connector, or file-artifact workflow notes when those target capabilities are available.
- Empty hook config -> plugin no-op `hooks/hooks.json` or no-op compatibility note.
- Active hook config -> plugin `hooks/hooks.json` only after schema/safety review; otherwise partial migration plan.

## Gemini-to-Codex Rules

- Convert `GEMINI.md` project guidance into `AGENTS.md`; do not treat it as a skill.
- Convert `gemini-extension.json` into a Codex plugin implementation plan or `.codex-plugin/plugin.json` only when fields are known.
- Convert Gemini `commands/*.toml` into workflow sections or Codex command notes.
- Convert Gemini subagent Markdown into `.codex/agents/*.toml` only for known fields.
- Treat Gemini policies and hooks as unsupported until Codex hook or policy equivalents are explicitly mapped.

## Audit Recommendations

In audit-only mode, recommend the concrete Codex staging layout and automatic port work without creating files:

- Codex plugin manifest: `ports/<source-name>/codex-marketplace/plugins/<plugin>/.codex-plugin/plugin.json`.
- Marketplace: `ports/<source-name>/codex-marketplace/.agents/plugins/marketplace.json` for plugin sources.
- Skills: plugin-contained `skills/<skill-name>/SKILL.md`, not global `~/.codex/skills`.
- Commands: plugin `references/command-map.md` and, for many commands, bundled `<plugin>-command-router` skill.
- Agent workflows: bundled `<agent-name>-workflow` skills plus orchestration references when needed.
- MCP setup: plugin `.mcp.json` plus `references/mcp-setup.md`.
- Dependencies: plugin `references/dependencies.md` for subscriptions, app provisioning, provider accounts, and credentials.
- Hooks: plugin `hooks/hooks.json` for no-op or compatible hooks, otherwise `references/hook-migration.md`.
- Unsupported behavior: plugin `references/unsupported.md`.

Only list credentials, subscriptions, MCP enablement, app provisioning, final install, and regulated human review as remaining manual steps.

## Port Mode Standard

When the source is a plugin or marketplace, use the deterministic staging helper:

```bash
python3 scripts/stage_port.py <source-path> --target-agent codex --output-root <workspace> --clean
```

For Codex plugin targets, do not install plugin-internal skills into `~/.codex/skills` as a substitute for plugin packaging. A flat global skill install is allowed only when the user explicitly asks for one or the source is a single skill/non-plugin bundle.

After staging, report the generated plugin or marketplace path and the exact Codex CLI command to expose it, usually `codex plugin marketplace add <marketplace-root>`. If the user asked to install for Codex Desktop local testing, prefer `scripts/install_codex_local_bundle.py <staged-codex-marketplace>` so marketplace registration, cache copies, and enabled plugin config are applied together. State that the user must restart Codex before bundled skills appear. Do not claim MCP servers, apps, or hooks are usable until required credentials/tooling are configured.

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
