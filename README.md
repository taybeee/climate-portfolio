# Sustainability & Climate Risk Portfolio

I built this to demonstrate how AI tooling -- specifically Claude Code -- can be used to accelerate real climate risk consulting work, not just summarise documents. It covers a full engagement lifecycle: data ingestion, GHG accounting, physical and transition risk, materiality, and disclosure.

## Simulated Client

Lumora Technologies B.V. is a consumer electronics manufacturer headquartered in Amsterdam with nine facilities across seven countries. FY2023 total emissions: 746,285.9 tCO2e (Scope 1+2+3, market-based).

## What I Built

| Step | Title | Status | Folder | Key Files |
|------|-------|--------|--------|-----------|
| 1 | AI Workflow Setup | Complete | `01-claude-setup/` | `workflow-explainer.md` -- explains the CLAUDE.md config and prompt engineering approach |
| 2 | Data Audit, GHG Accounting, SBTi | Complete | `02-data-audit/` | `lumora-data-quality-memo.md`, `lumora-ghg-inventory.csv`, `receipt-parser/parser.py`, `calculate-emissions.py`, `reconciliation-report.csv`, `sbti-gap-analysis.py`, `step2-summary-memo.md` |
| 3 | Physical Risk Assessment | In Progress | `03-physical-risk/` | Multi-hazard asset map, physical risk report |
| 4 | Transition Risk Assessment | Planned | `04-transition-risk/` | Integrated risk narrative |
| 5 | Double Materiality | Planned | `05-materiality/` | IRO register, materiality matrix |
| 6 | IFRS S2 / CSRD Disclosure | Planned | `06-disclosure/` | Full disclosure document |

## How to Navigate This Repo

Each numbered folder is a self-contained step with its own data inputs, code, and written outputs. Start with `CLAUDE.md` at the root to understand the methodology configuration that drives how Claude Code works across the project. Step 2 is the most code-heavy and is the best place to see the AI-assisted data pipeline in action: raw invoice text goes in, a reconciled and emission-factor-applied CSV comes out, and a gap analysis against SBTi targets is generated from that. Steps 3 onwards build on the same Lumora dataset and are designed to produce the kind of outputs a consultant would hand to a client or regulator. The `step2-summary-memo.md` in `02-data-audit/` is a good entry point if you want a narrative overview before diving into the code.

## Tools Used

- Claude Code and the Anthropic Python SDK (Claude claude-sonnet-4-6)
- Python 3 -- pandas-free, stdlib only (csv, pathlib, datetime)
- GHG Protocol Corporate Standard (Scope 1, 2, 3)
- Emission factors: IPCC AR6, IEA 2023, DEFRA 2023, EPA eGRID 2023
- SBTi Corporate Net-Zero Standard v1.2 and SBTi ICT Sector Guidance (GeSI)
- IPCC AR6 / SSP scenarios for physical risk (SSP1-2.6, SSP2-4.5, SSP5-8.5)
- NGFS scenarios for transition risk (Net Zero 2050, Delayed Transition, Current Policies)
- IFRS S2 and CSRD / ESRS E1 for disclosure

---

Taylor Black -- [LinkedIn](https://www.linkedin.com/in/taylor-black-97397280/)
