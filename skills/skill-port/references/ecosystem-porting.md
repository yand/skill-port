# Ecosystem Porting

Use this reference for large skill/plugin repositories that contain multiple skills, slash commands, agents, MCP configs, provider integrations, templates, examples, or install-time behavior.

## Source Shape

Large ecosystems often include:

- Multiple `SKILL.md` files across domains or workflows.
- Project instruction files such as `AGENTS.md`, `CLAUDE.md`, or target-specific equivalents.
- Slash commands or command prompts for common entrypoints.
- Agent/subagent definitions for role, routing, or orchestration behavior.
- Plugin manifests, marketplace metadata, setup scripts, or lifecycle hooks.
- MCP configs, provider integrations, app connectors, credentials, or subscription assumptions.
- Templates, examples, assets, and reusable scripts.

## Audit Defaults

When auditing a whole ecosystem and the user has not named a specific workflow, recommend a focused default bundle rather than asking whether to port everything:

- If the target supports plugins and the source is a plugin or marketplace, preserve plugin boundaries instead of flattening everything into global skills.
- Prefer workflows backed by clear `SKILL.md` files.
- Include command files only when their intent can be mapped to a target-agent trigger/workflow.
- Include shared references, templates, and examples only when directly used by selected workflows.
- Put provider/app dependencies into dependency notes.
- Put lifecycle hooks, marketplace install behavior, and orchestration behavior into unsupported-feature notes.
- Keep project instruction translation separate from skill staging.

Recommend whole-ecosystem porting only when the user explicitly asks for all skills, all plugins, all domains, all verticals, or full migration.

## Scope Heuristics

Choose a recommended scope without asking when the source structure is clear:

- **Single skill**: one `SKILL.md` and no plugin/command/agent/MCP structure.
- **Focused bundle**: multiple skills, commands, or integrations and no explicit request for all content.
- **Whole ecosystem**: explicit user request for all content, or a small ecosystem where all artifacts are closely coupled.
- **Unknown**: no standard skill structure or too little information.

## Command Mapping Defaults

Map slash commands automatically in audit recommendations and port mode:

- Command name -> inferred target trigger.
- Command body -> target workflow, `references/command-map.md` entry, or command-router skill.
- `$ARGUMENTS`-style placeholders -> instruction to parse the user request and ask only for missing required inputs.
- Frontmatter descriptions and argument hints -> target trigger text and required/optional input schema.
- Command chaining -> target workflow steps or unsupported orchestration notes.

Unknown commands should still be mapped to `references/command-map.md` with source path, inferred trigger, expected inputs, and target workflow notes.

When a source has many commands and the target lacks native slash-command packaging, recommend a small router skill that maps the familiar command names to the target workflows. The router should not execute commands; it should select the right skill/workflow and parse required inputs.

## Plugin Mapping Defaults

For targets with a plugin system, plugin-to-plugin migration is the preferred target for plugin sources:

- Source plugin manifest -> target plugin manifest.
- Source marketplace -> target marketplace catalog.
- Source plugin skills -> bundled target plugin skills.
- Source plugin MCP config -> bundled target plugin MCP config plus setup notes.
- Source plugin hooks -> bundled target plugin hooks only when compatible or no-op; otherwise migration notes.
- Source plugin commands -> bundled router/workflow skills plus command map.
- Source plugin assets/templates -> bundled assets or references.

For Codex, use `.codex-plugin/plugin.json`, plugin `skills/`, optional `.mcp.json`, optional `hooks/hooks.json`, optional `.app.json`, and marketplace entries in `.agents/plugins/marketplace.json`. Codex marketplace entries must use the documented `source`, `policy`, and `category` fields. For local staged marketplaces, run or tell the user to run `codex plugin marketplace add <marketplace-root>`, then stop. Tell the user to restart Codex and install/enable desired plugins from Codex's plugin directory or another official Codex UI/command when available. When the user explicitly asks for local Codex Desktop installation for testing, use the reviewed local-bundle installer instead of ad hoc config edits.

Do not install every plugin-internal skill as a global top-level skill unless the user explicitly asks for a flat skill install. Flat installs are acceptable for single-skill sources and small non-plugin bundles, but they are noisy for marketplaces and agent/plugin ecosystems.

In port mode, use the deterministic staging helper when available. If the helper's audit recommends a plugin or marketplace layout, follow that layout exactly; do not replace it with a flat `skills/` install because it is easier to script.

Do not claim that a Codex plugin is installed simply because files were copied under `plugins/` or a marketplace JSON was edited. Do not use hand-edited `[plugins."<name>@<marketplace>"] enabled = true` entries as an install substitute. For explicit local Codex Desktop installs, use `scripts/install_codex_local_bundle.py` so marketplace registration, cache copies, and config enablement are applied together.

## Agent and Orchestration Defaults

Do not collapse agent/plugin ecosystems to skill files only when named agents are part of the product:

- Agent role prompt -> workflow skill or target agent definition.
- Expected artifacts -> explicit workflow outputs.
- Guardrails and review stops -> preserved in the workflow skill.
- Component skill list -> references to target skills by target names.
- Tool allowlists -> required capability notes.
- Callable subagents, managed handoffs, dispatch, and tool-isolated workers -> orchestration recipe or unsupported/partial item unless the target runtime supports equivalent behavior.

If the target supports optional multi-agent delegation, describe it as an execution recipe, not as guaranteed automatic behavior.

## Hook Mapping Defaults

Classify hook files by behavior, not just path:

- Empty configs such as `[]`, `{}`, or `{ "hooks": {} }` -> no-op compatibility notes.
- Active hooks -> lifecycle migration plan with source event, matcher/scope, invoked command/tool, expected input/output contract, safety review, and target equivalent.
- Unknown hook syntax -> partial/manual, not active by default.

## Dependency Notes Defaults

Do not leave dependency design as a manual step. In audit mode, propose dependency notes; in port mode, stage them:

- `references/dependencies.md`: provider/app dependency inventory.
- `references/data-sources.md`: data provenance, required sources, and fallback rules.
- `references/mcp-setup.md` or target-specific variants such as `references/codex-mcp-setup.md`: target-agent MCP setup requirements without credentials.
- `references/unsupported.md`: plugin marketplace, lifecycle, app provisioning, or orchestration behavior that is not natively available.

Provider credentials, subscriptions, app provisioning, and MCP/tool enablement remain external manual setup.

## Safety Requirements

- Preserve source disclaimers, human-review requirements, and safety limits.
- Do not convert regulated professional advice workflows into advice-giving workflows.
- Do not substitute weaker public data sources when the source explicitly requires controlled or proprietary data.
- Do not package secrets, credentials, tokens, or account-specific configuration.
