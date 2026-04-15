# Sustainability & Climate Risk Portfolio

An AI-augmented sustainability and climate risk portfolio demonstrating end-to-end consulting workflows built with Claude Code. The project simulates a full client engagement spanning GHG accounting, SBTi target-setting, physical and transition risk assessment, double materiality, and IFRS S2/CSRD disclosure. Each step produces consultant-grade deliverables -- structured data outputs, reconciled inventories, scored risk assessments, and regulator-ready narrative -- using reproducible Python tooling and a configured methodology file (CLAUDE.md) that encodes professional standards directly into the AI workflow.

## Simulated Client

Lumora Technologies B.V. is a consumer electronics manufacturer headquartered in Amsterdam, operating nine facilities across seven countries including manufacturing sites in Vietnam, Malaysia, Mexico, and the Netherlands. The company has approximately 4.2 million units of annual product sales and a total FY2023 GHG footprint of 746,285.9 tCO2e (Scope 1+2+3, market-based), with Scope 3 representing 92.5% of total emissions. Lumora is used throughout this portfolio as a realistic, data-rich client context for testing AI-assisted climate risk workflows against the complexity of real-world engagements.

## Project Steps

| Step | Title | Status | Deliverables |
|------|-------|--------|--------------|
| 1 | AI-Augmented Workflow Setup | Complete | CLAUDE.md methodology config, workflow explainer |
| 2 | Data Audit, GHG Accounting and SBTi Gap Analysis | Complete | Data quality memo, GHG inventory, RAG receipt parser, emissions calculator, inventory reconciliation, SBTi gap analysis, Step 2 summary memo |
| 3 | Physical Risk Assessment and Multi-Hazard Map | In Progress | Physical risk assessment report, interactive multi-hazard asset map |
| 4 | Transition Risk Assessment and Integrated Narrative | Planned | Transition risk assessment, integrated physical and transition narrative |
| 5 | Double Materiality Assessment | Planned | IRO register, scored materiality matrix, topic narratives |
| 6 | IFRS S2 / CSRD Disclosure Narrative | Planned | Full climate disclosure document aligned to IFRS S2 and ESRS E1 |

## Tools and Methodology

| Category | Detail |
|----------|--------|
| AI Tooling | Claude Code (Anthropic), Claude API with prompt caching and few-shot prompting |
| Language | Python 3 |
| GHG Accounting | GHG Protocol Corporate Standard (Scope 1, 2, 3) |
| Emission Factors | IPCC AR6, IEA 2023, DEFRA 2023, EPA eGRID 2023 |
| Target-Setting | SBTi Corporate Net-Zero Standard v1.2, SBTi ICT Sector Guidance (GeSI) |
| Physical Risk | IPCC AR6 / SSP scenarios (SSP1-2.6, SSP2-4.5, SSP5-8.5), ND-GAIN Country Index |
| Transition Risk | NGFS scenarios (Net Zero 2050, Delayed Transition, Current Policies) |
| Disclosure | IFRS S2, CSRD / ESRS E1, TCFD |

---

Taylor Black | [LinkedIn](https://www.linkedin.com/in/taylor-black-97397280/)
