# skill-port

`skill-port` is an agent skill for auditing and porting AI agent skills/plugins between agent ecosystems. It is optimized for Claude Code, Claude Cowork, and Claude plugin sources targeting Codex, while keeping the workflow adapter-based for other targets.

The installable skill lives at [`skills/skill-port`](skills/skill-port/SKILL.md).

## What It Does

- Audits skills, plugin folders, command bundles, agent bundles, and MCP-backed plugin repos.
- Reports portability, target-agent compatibility, security findings, dependencies, and manual setup.
- Stages ported output under target-agent naming instead of mutating installed skill directories.
- Helps adapt Claude-specific artifacts such as slash commands, Cowork plugins, Managed Agent cookbooks, and MCP connector notes for Codex.

## Install

From this repository:

```bash
npx skills add . --skill skill-port
```

From GitHub after publishing:

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
Use skill-port to audit this Claude Code plugin for Codex compatibility: ./vendor/example-plugin
```

```text
Use skill-port to port ./my-claude-skill to Codex and stage the output under target-agent naming.
```

The deterministic helper can also be run directly:

```bash
python3 skills/skill-port/scripts/audit_skill.py ./path/to/source --target-agent codex --format markdown
```

## Safety Model

`skill-port` is read-only by default:

- It does not install source skills/plugins during audit.
- It does not run source scripts, package managers, lifecycle hooks, or plugin commands.
- It does not write into global or project agent install directories unless explicitly requested.
- It flags secret-like values, destructive commands, shell execution, network calls, lifecycle hooks, credential access, MCP configs, hidden files, binaries, and large files.

## Repository Layout

```text
skills/skill-port/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/audit_skill.py
```

This uses a standard `skills/<name>/` layout so skill indexes and installers can discover the skill without relying on recursive fallback.

## Index Readiness

The skill follows the Agent Skills shape: a directory containing `SKILL.md` with `name` and `description` frontmatter plus optional `scripts/` and `references/`.

Before publishing, run:

```bash
python3 skills/skill-port/scripts/audit_skill.py skills/skill-port --target-agent codex --format markdown
npx skills add . --list
```

The `skills.sh` directory ranks installable skills from CLI telemetry and recommends a README explaining usage. Its audits can still flag risks, so users should review reports before installing any third-party skill.

## Sources

- Agent Skills specification: https://agentskills.io/specification
- skills.sh documentation: https://www.skills.sh/docs
- skills CLI documentation: https://www.skills.sh/docs/cli
