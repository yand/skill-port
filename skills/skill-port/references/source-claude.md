# Claude Source Adapter

Use this reference when the source is a Claude Code skill, Claude Code plugin, Claude Cowork plugin, slash command bundle, agent bundle, hook config, MCP-backed plugin, or Claude Managed Agent cookbook.

## Artifact Mapping

| Claude artifact | Target handling |
| --- | --- |
| `SKILL.md` | Usually portable after frontmatter, wording, and path cleanup. |
| `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` | Treat as project instructions. Translate or bridge to target project guidance such as `AGENTS.md`; do not package as a skill. |
| `.claude/skills/<name>/SKILL.md` | Port to `skills/<target-agent>/<name>/SKILL.md` for a single skill. |
| `plugins/**/skills/<name>/SKILL.md` | For Codex plugin targets, keep skills bundled under the corresponding plugin `skills/` directory. Do not flatten plugin-internal skills into global skills unless explicitly requested. |
| `.claude/commands/*.md` or `commands/*.md` | Convert command intent into trigger text, workflow sections, or prompt snippets. Do not claim native slash-command support unless the target has it. |
| `.claude/agents/*.md` or `agents/*.md` | Convert procedural parts into workflow skills or target agent definitions. Keep role/runtime/subagent behavior as target-specific notes unless supported. |
| `.claude/settings*.json` hooks, `hooks/hooks.json` | Distinguish empty/no-op configs from active hooks. Empty configs are compatibility notes; active hooks need target lifecycle mapping before activation. |
| `.claude-plugin/`, `plugin.json`, `manifest.json` | For Codex targets, translate to `.codex-plugin/plugin.json` when the source is a plugin. Preserve metadata and point at bundled skills, MCPs, apps, and hooks. |
| `.claude-plugin/marketplace.json` | For Codex targets, translate to a Codex-valid `.agents/plugins/marketplace.json` with one `source`/`policy`/`category` entry per staged plugin when possible. |
| `.mcp.json` or MCP server configs | Treat as dependency-bound but mappable. For Codex plugin targets, generate plugin `.mcp.json` plus setup notes. Capture server names, endpoint type/URL, auth requirements, likely tool prefixes, and target setup/config snippets with placeholders. |
| Managed Agent `agent.yaml` and callable agents | Treat as orchestration behavior. Port reusable instructions into workflow skills or recipes; report subagent handoff, scoped tools, and review gates separately. |
| Cowork dispatch/project behavior | Treat as Claude/Cowork-specific unless the target environment provides a matching workflow. |

## Rewrite Rules

- Replace "Claude" wording with target-neutral wording unless the behavior is actually Claude-specific.
- Preserve domain expertise, examples, templates, and quality checks.
- Preserve safety disclaimers and human-review requirements.
- Convert `$ARGUMENTS` into explicit instruction parsing or a short user question.
- Convert command `argument-hint` frontmatter into required/optional input handling in the target workflow.
- Convert `!` command-injection lines into explicit workflow steps or scripts only after security review; otherwise mark partial/manual.
- Remove assumptions about `.claude` paths from reusable instructions.
- Keep MCP/provider access as dependency notes, not as installed capabilities.
- When source instructions mention Claude/Cowork-specific MCP tool names such as `mcp__provider__*`, map them to target MCP/tool names only if configured; otherwise preserve them as required capability notes and provide fallback behavior if the source allows one.
- If a source contains plugin metadata and skills, prefer target plugin bundles over a flat skill-only copy when the target supports plugins.
- For multi-plugin repositories, preserve plugin boundaries by staging one target plugin per source plugin or marketplace entry. Avoid installing synced/bundled duplicate skills globally.

## Claude-Specific Skill Signals

Flag these because they can make a skill lossy when ported:

- Dynamic context injection with shell command syntax.
- Invocation control such as user-only/model-only activation.
- Path-scoped activation.
- Forked context or named subagent execution.
- Claude tool allowlists/disallowlists.
- Skill-level hooks.
- Agent/subagent fields in frontmatter.
- Plugin marketplace installation, automatic command registration, or dispatch behavior.
- Managed-agent handoff events, callable agents, or tool-isolated workers.

## Classification Defaults

- Plain markdown workflows are usually portable.
- Scripts are portable only after security review and dependency inventory.
- Slash commands need adaptation into target entrypoints; they should not remain only as passive references when they represent primary user workflows.
- Project instruction files need translation/bridging, not skill conversion.
- Empty hooks are no-op source artifacts. Active hooks, auto-install behavior, Cowork dispatch, and Managed Agent subagent routing are not portable by default.
- Claude plugin sources should default to plugin-to-plugin migration for targets that support plugins, especially Codex.
