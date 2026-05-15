# skill-port

[![Install with skills.sh](https://img.shields.io/badge/install%20with-skills.sh-111827)](https://www.skills.sh/docs/cli)

`skill-port` is an Agent Skills portability auditor for developers who want to reuse AI agent skills, plugins, slash commands, subagents, MCP configs, and workflow packs across Claude Code, Codex, Gemini CLI, Google Antigravity, and other Agent Skills-compatible runtimes.

Use it when a Claude Code plugin does not work in Codex, a Codex skill needs to be adapted for Claude Code, a Gemini CLI extension or Antigravity skill/rule bundle needs a portability review, or a skill repository needs a deterministic compatibility and security report before installation.

The installable skill lives at [`skills/skill-port`](skills/skill-port/SKILL.md).

## Problems It Solves

- "Can I use this Claude Code skill or plugin in Codex?"
- "What needs to change before this Codex skill works in Claude Code?"
- "How portable is this Gemini CLI extension?"
- "Can this Antigravity skill, rule, workflow, or MCP setup be reused elsewhere?"
- "Which parts of this agent plugin are standard Agent Skills, and which parts are vendor-specific?"
- "Does this skill contain risky scripts, hooks, network calls, secret-like values, or destructive commands?"
- "Where should ported files be staged without mutating my global agent install?"

## Install with skills.sh

```bash
npx skills add yand/skill-port --skill skill-port
```

The `skills.sh` CLI is the main discovery path for public skill directories and leaderboards.

## What It Does

- Audits Agent Skills, Claude Code skills/plugins, Codex skills/plugins, Gemini CLI skills/extensions, Antigravity skills/rules/workflows, command bundles, agent bundles, and MCP-backed plugin repos.
- Reports portability, target-agent compatibility, source/target file mapping, security findings, dependencies, and manual setup.
- Stages ported output under target-agent naming instead of mutating installed skill directories.
- Helps adapt source-specific artifacts such as slash commands, Codex custom agents, Gemini extensions, Antigravity rules/workflows, Cowork plugins, managed-agent cookbooks, hooks, policies, and MCP connector setup.
- Maps non-skill plugin layers into target-native plans where possible: command maps/router skills, workflow skills for named agents, MCP setup snippets with credential placeholders, and no-op versus active hook treatment.

## Common Searches

People looking for this skill may describe the problem as:

- Claude Code plugin to Codex
- Claude skill to Codex skill
- Codex skill to Claude Code
- Gemini CLI extension portability
- Antigravity skill portability
- Antigravity MCP config audit
- Agent Skills converter
- AI agent skill adapter
- MCP plugin portability audit
- slash command migration for AI coding agents
- subagent portability between Claude Code, Codex, Gemini CLI, and Antigravity
- skills.sh compatible skill audit

## Install

From this repository:

```bash
npx skills add . --skill skill-port
```

From GitHub:

```bash
npx skills add yand/skill-port --skill skill-port
```

The CLI detects the current agent environment and installs into that agent's supported skill location. Review the CLI output before using the skill.

## Usage

Ask your agent to use `skill-port` in one of three modes:

- `audit-only`: inspect a source and produce a compatibility/security report.
- `port`: stage target-agent files plus the report.
- `case-study`: analyze a large plugin ecosystem and recommend what to port, split, ignore, or document as dependencies.

Example prompts:

```text
Use skill-port to audit this agent skill before I install it: ./some-skill
```

```text
Use skill-port to audit this Claude Code plugin for Codex compatibility: ./vendor/example-plugin
```

```text
Use skill-port to port ./my-claude-skill to Codex and stage the output under target-agent naming.
```

```text
Use skill-port to audit this Codex plugin for Claude Code compatibility: ./vendor/codex-plugin
```

```text
Use skill-port to audit this Gemini extension and recommend a Codex target layout: ./vendor/gemini-extension
```

```text
Use skill-port to audit this Antigravity skill/rule bundle for Claude Code compatibility: ./vendor/antigravity-bundle
```

The deterministic helper can also be run directly:

```bash
python3 skills/skill-port/scripts/audit_skill.py ./path/to/source --target-agent codex --format markdown
python3 skills/skill-port/scripts/audit_skill.py ./path/to/source --target-agent claude --format markdown
python3 skills/skill-port/scripts/audit_skill.py ./path/to/source --target-agent gemini --format markdown
python3 skills/skill-port/scripts/audit_skill.py ./path/to/source --target-agent antigravity --format markdown
```

If `--target-agent` is omitted, the helper first honors explicit runtime self-identification such as `AGENT_RUNTIME`, `AGENT_NAME`, `CURRENT_AGENT`, or `HOST_AGENT`, then falls back to high-confidence environment variables and conservative heuristics. Known aliases normalize to `codex`, `claude`, `gemini`, or `antigravity`.

## Safety Model

`skill-port` is read-only by default:

- It does not install source skills/plugins during audit.
- It does not run source scripts, package managers, lifecycle hooks, or plugin commands.
- It does not make network requests from the bundled auditor.
- It does not write into global or project agent install directories unless explicitly requested.
- The deterministic auditor writes only when `--output <path>` is explicitly provided.
- It flags secret-like values, destructive commands, shell execution, network calls, lifecycle hooks, credential access, MCP configs, hidden files, binaries, and large files.

See [SECURITY.md](SECURITY.md) for the full safety boundary and reporting guidance.

## Repository Layout

```text
skills/skill-port/
  SKILL.md
  agents/openai.yaml
  references/               # source/target adapters, security, reporting, location policy
  scripts/audit_skill.py
```

This uses a standard `skills/<name>/` layout so skill indexes and installers can discover the skill without relying on recursive fallback. Adapter references currently cover Claude Code, Codex, Gemini CLI, and Antigravity as both sources and targets.

## Index Readiness

The skill follows the Agent Skills shape: a directory containing `SKILL.md` with `name` and `description` frontmatter plus optional `scripts/` and `references/`.

To help `skills.sh` discover and rank the skill, install it from GitHub with telemetry-enabled CLI defaults:

```bash
npx skills add yand/skill-port --skill skill-port
```

Before publishing, run:

```bash
python3 skills/skill-port/scripts/audit_skill.py skills/skill-port --target-agent codex --format markdown
npx skills add . --list
```

## License

Licensed under the [Apache License 2.0](LICENSE). Attribution notices are provided in [NOTICE](NOTICE).

## Sources

- Agent Skills specification: https://agentskills.io/specification
- skills.sh documentation: https://www.skills.sh/docs
- skills CLI documentation: https://www.skills.sh/docs/cli
