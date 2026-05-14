# Security Policy

`skill-port` is designed to inspect untrusted agent skills and plugin folders without executing them.

## Safety Boundary

The bundled auditor, `skills/skill-port/scripts/audit_skill.py`, is read-only by default:

- It does not install source skills or plugins.
- It does not run source scripts, package managers, lifecycle hooks, plugin commands, or shell commands.
- It does not make network requests.
- It does not read outside the source directory except for normal filesystem metadata needed to walk the selected tree.
- It writes only when `--output <path>` is explicitly provided.
- It redacts secret-like matches in its report.

The script computes file inventories, hashes, compatibility signals, and pattern-based security findings. Findings are advisory and do not prove a source is safe.

## User Responsibilities

Before installing or running any third-party skill/plugin:

- Review the audit report.
- Review any scripts, hooks, MCP configs, and dependency notes.
- Keep credentials, tokens, provider subscriptions, and app provisioning outside the skill package.
- Use the target agent's normal trust and installation prompts.

## Reporting Issues

Open a GitHub issue for suspected vulnerabilities or unsafe behavior. Do not include live secrets, tokens, private keys, or proprietary source content in public reports.
