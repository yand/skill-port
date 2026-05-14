# Portability Model

Use this reference before porting between agent ecosystems. Model the source as layers, then decide whether each layer is direct, translated, partial, unsupported, or manual.

## Layers

| Layer | Examples | Porting rule |
| --- | --- | --- |
| Project instructions | `AGENTS.md`, `CLAUDE.md`, nested override files | Translate or bridge; do not treat as skills. |
| Skills | `SKILL.md`, `scripts/`, `references/`, `assets/` | Usually the most portable layer. |
| Commands | Slash commands, command prompts, user-triggered workflows | Translate into target triggers/workflows. |
| Agents | Claude subagents, Codex custom agents, managed agents | Convert only known configuration fields; otherwise document as partial/unsupported. |
| Plugins | Plugin manifests, marketplaces, install metadata | Rebuild for target package format; do not rename blindly. |
| MCP/tools | `.mcp.json`, config files, tool manifests | Convert simple configs when target format is known; credentials/setup remain manual. |
| Hooks | Lifecycle scripts/checks | Treat as advanced and risky; convert only with known event/matcher/IO mapping. |

## Conversion Status

- `direct`: safe copy with path/name cleanup only.
- `translated`: known mapping with target-specific syntax changes.
- `partial`: useful target output can be staged, but behavior is not equivalent.
- `unsupported`: preserve as notes; do not activate.
- `manual`: requires user credentials, install approval, provider setup, or policy decisions.

## Normalized Internal Model

Think in terms of a portable model before writing target files:

```text
source package
  -> project instructions
  -> skills
  -> commands
  -> agents
  -> plugin metadata
  -> MCP/tool dependencies
  -> hooks/lifecycle behavior
  -> compatibility report
  -> target package
```

This prevents fake lossless conversion. The report should say what is direct, translated, partial, unsupported, and manual.

## Key Rules

- Project instructions are behavior context, not reusable workflow skills.
- Skills are portable only after checking frontmatter, dynamic context syntax, path assumptions, scripts, and target-specific metadata.
- Agents/subagents are configuration. Do not collapse them into skills unless only procedural instructions remain.
- Plugin manifests are target-specific. Build a new target manifest or document a plugin implementation plan.
- MCP is conceptually shared but config, auth, scope, and trust semantics differ by agent.
- Hooks are not portable as text; lifecycle events, matchers, JSON input, and output semantics must be mapped explicitly.
