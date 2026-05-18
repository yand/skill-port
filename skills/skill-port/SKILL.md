---
name: skill-port
description: Audit and port AI agent skills, Claude Code skills/plugins, Codex skills/plugins, Gemini CLI skills/extensions, Antigravity skills/rules/workflows, slash commands, agents, hooks, policies, MCP-backed plugins, and similar skill repositories across target agents. Use when asked to assess portability, generate a compatibility/security report, stage a port under target-agent naming, or adapt agent-specific skills/plugins for another runtime.
license: Apache-2.0
metadata:
  author: Yaniv Daniel
  homepage: https://github.com/yand/skill-port
---

# Skill Port

Use this skill to audit or port agent skills and plugin ecosystems. It supports Claude Code, Codex, Gemini CLI, Google Antigravity, and Agent Skills-compatible sources and targets through an adapter-based workflow.

## Operating Modes

- **audit-only**: inspect the source and produce a deterministic compatibility/security report. Do not create ported files.
- **port**: inspect the source, stage target-agent files, and produce the same report.
- **case-study**: analyze a large ecosystem and recommend what to port, split, ignore, or keep as dependency notes.

Default to `audit-only` when the user's request is unclear or security-sensitive. In audit-only mode, be decisive: recommend a concrete port scope, target layout, command mapping plan, and next port command without creating files.

## Safety Rules

- Do not install a source skill/plugin as part of auditing or porting.
- Do not run source scripts, package managers, install lifecycle hooks, or plugin commands unless the user explicitly asks after reviewing the audit.
- Do not write into global or project agent install directories unless the user explicitly asks.
- Stage output under target-agent naming:
  - Single skill: `skills/<target-agent>/<skill-name>/`
  - Multi-skill/plugin source: `ports/<source-name>/<target-agent>/`
- Treat installation as a separate final step using the target agent's normal installer.
- Preserve warnings, legal disclaimers, human-review requirements, and safety limits from the source.

## Workflow

1. **Identify source and target**
   - Determine source path or URL, source agent/ecosystem, target agent, and requested mode.
   - If the target agent is not specified, first use the active assistant/runtime's self-identification when available. Normalize known aliases for Codex, Claude Code, Gemini CLI, and Antigravity.
   - For the deterministic helper, prefer `--target-agent`; otherwise it checks explicit runtime hints such as `AGENT_RUNTIME`, `AGENT_NAME`, `CURRENT_AGENT`, or `HOST_AGENT`, then high-confidence environment variables, then conservative substring fallback.
   - Keep runtime inference separate from source ecosystem detection: a source may contain Gemini or Antigravity files even when the active target agent is Codex.
   - For remote URLs, clone/fetch only after user approval or explicit execution request; otherwise document the needed command.
   - For expensive scans, ask the user to run focused commands and share output.

2. **Run inventory**
   - Prefer `scripts/audit_skill.py` for deterministic local inspection.
   - If the source is large, run it on the narrowest useful directory first.
   - Read source-specific references only as needed:
     - Portability model: `references/portability-model.md`
     - Claude sources: `references/source-claude.md`
     - Codex sources: `references/source-codex.md`
     - Gemini sources: `references/source-gemini.md`
     - Antigravity sources: `references/source-antigravity.md`
     - Codex targets: `references/target-codex.md`
     - Claude targets: `references/target-claude.md`
     - Gemini targets: `references/target-gemini.md`
     - Antigravity targets: `references/target-antigravity.md`
     - Large ecosystems: `references/ecosystem-porting.md`
     - Location policy: `references/locations.md`
     - Security review: `references/security.md`

3. **Classify artifacts**
   - First classify by layer: project instructions, skills, commands, agents, plugins, MCP/tools, hooks, assets/scripts.
   - Portable: agent-neutral `SKILL.md`, references, examples, assets, templates.
   - Needs adaptation: slash commands, agent prompts, Claude wording, target-specific frontmatter.
   - Dependency-bound: MCP configs, external APIs, subscriptions, app connectors, credentials.
   - Target-native candidates: plugin manifests/marketplaces, bundled skills, command entrypoints, agent workflows, MCP setup snippets, app/document connector mappings, and no-op hook records when the target has a reasonable equivalent or documentation surface.
   - Unsupported: active lifecycle hooks, automatic plugin installation, automatic dispatch, managed-agent orchestration, policy engines, and target-specific extension behavior unless a target equivalent is available.
   - Distinguish empty/no-op hook configs from active hooks. Empty hook files should be recorded as no-op source artifacts, not treated as blockers.
   - When the source and target both support plugins, prefer plugin-to-plugin migration over a flat skill install.
   - Mark each mapped item as `direct`, `translated`, `partial`, `unsupported`, or `manual`.

4. **Port only when requested**
   - Prefer `scripts/stage_port.py` for deterministic staging. It consumes the same audit mapping and writes the target layout without installing anything.
   - Create target-agent skill or plugin folders in the staging location.
   - Rewrite frontmatter for the target agent.
   - For plugin sources targeting Codex, stage a Codex plugin or Codex marketplace with `.codex-plugin/plugin.json`, bundled `skills/`, optional `.mcp.json`, optional `.app.json`, optional `hooks/hooks.json`, and `references/`.
   - Do not mirror plugin-internal skills into global `~/.codex/skills` unless the user explicitly asks for a flat skill install.
   - For Codex plugin sources, staging is not installation. To expose a staged marketplace to Codex, use `codex plugin marketplace add <marketplace-root>`, then stop. Tell the user to restart Codex and install/enable desired plugins from Codex's plugin directory or another official Codex UI/command when available.
   - For Codex Desktop local plugin installation, use Codex's private local bundle pattern when the user explicitly asks to install: run `scripts/install_codex_local_bundle.py <staged-codex-marketplace>` after reviewing staged files. This registers the marketplace, copies plugins into `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>`, enables `[features] plugins = true`, and marks each plugin enabled in `~/.codex/config.toml`.
   - Do not edit `~/.codex/config.toml` by ad hoc string appends. If local installation is explicitly requested, use the deterministic local bundle installer so config changes, cache copies, and marketplace registration stay consistent.
   - Do not call marketplace registration alone "installed." A local Codex plugin bundle install requires marketplace registration, plugin cache copy, and enabled plugin config.
   - Convert slash-command intent into target-native entrypoints: trigger text, workflow sections, command maps, or router skills where the target has no native slash-command package format.
   - Convert procedural agent/subagent prompts into workflow skills or orchestration recipes. Preserve automatic dispatch, tool isolation, and managed handoff behavior as explicit limitations unless the target supports them.
   - Convert MCP configs into target MCP files, setup notes, or config snippets with credential placeholders. Provider credentials, app provisioning, subscriptions, and final enablement stay manual.
   - Create dependency and unsupported-feature notes for provider credentials, app connectors, active lifecycle hooks, and orchestration behavior.
   - Keep unsupported features in dependency notes or a compatibility report; do not pretend they work.

5. **Report**
   - Follow `references/report-schema.md`.
   - Include target compatibility, recommended scope, proposed target layout, layer summary, conversion status, command mapping plan, agent/workflow mapping plan, MCP setup plan, no-op versus active hook treatment, dependency-bound items, unsupported items, security findings, output paths, install commands, and remaining manual steps.

## Useful Commands

```bash
python3 scripts/audit_skill.py <source-path> --target-agent codex
python3 scripts/audit_skill.py <source-path> --target-agent codex --format markdown
python3 scripts/audit_skill.py <source-path> --target-agent claude --format markdown
python3 scripts/audit_skill.py <source-path> --target-agent gemini --format markdown
python3 scripts/audit_skill.py <source-path> --target-agent antigravity --format markdown
python3 scripts/audit_skill.py <source-path> --target-agent codex --output report.json
python3 scripts/stage_port.py <source-path> --target-agent codex --output-root . --clean
```

## Output Standard

For every audit or port, state:

- Source inspected and target agent.
- Whether files were created and where.
- Compatibility summary.
- Layer summary and conversion status summary.
- Recommended scope and proposed target layout.
- Automatic work that can be done in port mode.
- Security findings that affect installation or trust.
- Manual setup still required, limited to credentials, subscriptions, MCP/tool enablement, app connector provisioning, regulated human review, or target-agent installation.
- For Codex plugin ports, distinguish three states clearly: staged files, marketplace exposed through `codex plugin marketplace add`, and plugin installed/enabled. Do not use ad hoc `~/.codex/config.toml` edits as an install substitute; when the user explicitly asks for local Codex Desktop installation, use `scripts/install_codex_local_bundle.py` so marketplace registration, cache copies, and config enablement stay consistent.
