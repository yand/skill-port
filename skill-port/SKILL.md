---
name: skill-port
description: Audit and port AI agent skills, Claude Code skills, Claude Cowork plugins, slash commands, agents, MCP-backed plugins, and similar skill repositories to Codex or another target agent. Use when asked to assess portability, generate a compatibility/security report, stage a port under target-agent naming, or adapt Claude-oriented skills/plugins such as anthropics/financial-services for Codex.
---

# Skill Port

Use this skill to audit or port agent skills and plugin ecosystems. It is optimized for Claude/Cowork/Claude Code sources and Codex targets, but the workflow is adapter-based so future targets can be added without changing the core process.

## Operating Modes

- **audit-only**: inspect the source and produce a deterministic compatibility/security report. Do not create ported files.
- **port**: inspect the source, stage target-agent files, and produce the same report.
- **case-study**: analyze a large ecosystem and recommend what to port, split, ignore, or keep as dependency notes.

Default to `audit-only` when the user's request is unclear or security-sensitive.

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
   - For remote URLs, clone/fetch only after user approval or explicit execution request; otherwise document the needed command.
   - For expensive scans, ask the user to run focused commands and share output.

2. **Run inventory**
   - Prefer `scripts/audit_skill.py` for deterministic local inspection.
   - If the source is large, run it on the narrowest useful directory first.
   - Read source-specific references only as needed:
     - Claude sources: `references/source-claude.md`
     - Codex targets: `references/target-codex.md`
     - Location policy: `references/locations.md`
     - Security review: `references/security.md`

3. **Classify artifacts**
   - Portable: agent-neutral `SKILL.md`, references, examples, assets, templates.
   - Needs adaptation: slash commands, agent prompts, Claude wording, target-specific frontmatter.
   - Dependency-bound: MCP configs, external APIs, subscriptions, app connectors, credentials.
   - Unsupported: lifecycle hooks, automatic plugin installation, Cowork dispatch, Managed Agent orchestration unless a target equivalent is available.

4. **Port only when requested**
   - Create target-agent skill folders in the staging location.
   - Rewrite frontmatter for the target agent.
   - Convert slash-command intent into trigger text or workflow sections.
   - Keep unsupported features in dependency notes or a compatibility report; do not pretend they work.

5. **Report**
   - Follow `references/report-schema.md`.
   - Include target compatibility, porting map, security findings, output paths, install commands, and manual steps.
   - For `anthropics/financial-services`, also read `references/financial-services-case.md`.

## Useful Commands

```bash
python3 skill-port/scripts/audit_skill.py <source-path> --target-agent codex
python3 skill-port/scripts/audit_skill.py <source-path> --target-agent codex --format markdown
python3 skill-port/scripts/audit_skill.py <source-path> --target-agent codex --output report.json
```

## Output Standard

For every audit or port, state:

- Source inspected and target agent.
- Whether files were created and where.
- Compatibility summary.
- Security findings that affect installation or trust.
- Manual setup still required, especially credentials, MCP servers, app connectors, or target-agent installation.
