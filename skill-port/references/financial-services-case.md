# Anthropic Financial Services Case

Use this reference for `anthropics/financial-services` or similar financial-services skill/plugin ecosystems.

## Source Shape

The repository includes:

- Named agent plugins for workflows like pitch books, market research, earnings review, model building, reconciliation, and KYC.
- Vertical plugins for financial analysis, investment banking, equity research, private equity, wealth management, fund admin, operations, and partner data providers.
- `SKILL.md` files containing reusable financial workflows.
- Slash commands such as `/comps`, `/dcf`, `/lbo`, `/earnings`, `/ic-memo`, and similar command entrypoints.
- MCP connector configuration for data providers such as FactSet, Morningstar, S&P/Kensho, Daloopa, LSEG, PitchBook, and others.
- Managed Agent cookbooks and Claude/Cowork plugin behavior.

## Porting Guidance

- Good Codex skill candidates: comps analysis, DCF, LBO, 3-statement model, Excel audit, earnings analysis, IC memo, thesis tracking, buyer list, client review, tax-loss harvesting.
- Needs adaptation: slash commands, Claude-specific wording, plugin manifests, command routing.
- Dependency-bound: MCP data providers, subscription data, Excel/PowerPoint/app integrations, provider credentials.
- Unsupported by default: Cowork dispatch, Claude plugin marketplace install, Claude Managed Agent orchestration, callable subagents.

## Safety Requirements

- Preserve disclaimers that outputs are analyst work product for qualified human review.
- Do not make investment, legal, tax, or accounting recommendations.
- Treat financial data quality and provenance as required workflow content.
- Do not substitute public web search for institutional data when the source skill explicitly requires controlled data providers.
