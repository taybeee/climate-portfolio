# Memorandum

**To:** Lumora Technologies B.V. Sustainability Team
**From:** Taylor Black, Climate Risk & Sustainability
**Date:** April 2024
**Subject:** Step 2 Findings — GHG Data Audit, Emissions Accounting, Inventory Reconciliation, and SBTi Gap Analysis
**Classification:** Internal Working Document

---

## Executive Summary

This memo consolidates the four analytical workstreams completed in Step 2 of Lumora's climate risk engagement. Taken together, they establish a defensible FY2023 GHG baseline, identify the data quality gaps that must be resolved before formal disclosure, and quantify the emission reductions required to align with SBTi's Corporate Net-Zero Standard.

**Key findings:**

- Lumora's FY2023 GHG inventory totals **746,285.9 tCO2e** (Scope 1+2+3, market-based). Scope 3 constitutes 92.5% of total emissions, making supply chain and product use the dominant decarbonisation challenge.
- The RAG receipt parser processed five invoices across four facilities and achieved four out of five High confidence extractions, demonstrating reliable structured data ingestion from heterogeneous source documents. One reconciliation-critical anomaly was surfaced — a false positive billing overlap on F02 — and two deeper data inconsistencies were uncovered that require resolution before the FY2023 base year is locked.
- Under the SBTi Corporate Net-Zero Standard, Lumora must reduce total emissions by **226,897.2 tCO2e (30.4%)** by 2030, requiring average annual reductions of **32,413.9 tCO2e per year**. Scope 2 market-based emissions represent the fastest near-term abatement lever; Category 1 purchased goods data quality is the binding constraint on base year credibility.

---

## 1. RAG Receipt Parser

### Purpose and Design

The receipt parser was built to demonstrate automated, AI-assisted extraction of energy consumption data from unstructured supplier invoices — replacing manual re-keying as a source of transcription error and audit trail gaps. The parser uses the Anthropic Claude API with few-shot prompting and prompt caching, applies structured anomaly detection logic, and outputs a confidence-scored CSV record per invoice suitable for direct ingestion into the emissions calculator.

Five invoices were selected to test a range of real-world parsing challenges: Dutch, Vietnamese, and Mexican number formatting conventions; multi-month billing periods; energy unit diversity (kWh, m³, GJ, litres); currency diversity (EUR, VND, MXN); and a deliberate disambiguation challenge (active vs reactive energy on the Vietnamese invoice).

### Results

| Invoice | Facility | Energy Type | Quantity | Unit | Confidence | Key Parsing Challenge |
|---|---|---|---|---|---|---|
| invoice-F01-electricity-jan2023 | Amsterdam HQ | Electricity | 310,450 | kWh | High | Market-based vs location-based Scope 2 flag |
| invoice-F02-diesel-q1-2023 | Eindhoven Mfg | Diesel | 12,400 | L | High | Dutch thousands separator (12.400 -> 12,400) |
| invoice-F02-gas-q1-2023 | Eindhoven Mfg | Natural gas | 172,510 | m3 | Medium | Dutch format + billing period overlap flag |
| invoice-F04-electricity-apr2023 | HCMC Mfg | Electricity | 2,883,333 | kWh | High | Active vs reactive energy disambiguation |
| invoice-F06-gas-jan-feb-2023 | Monterrey Mfg | Natural gas | 10,980.15 | GJ | High | European decimal format; 2-month period |

Four of five invoices were extracted at High confidence. The single Medium confidence rating on F02 natural gas reflects an automated BILLING_PERIOD_OVERLAP flag triggered when both the Q1 diesel and Q1 gas invoices were processed for the same facility and period — an expected condition for multi-stream energy procurement that is correctly classified as a false positive in the reconciliation notes.

Three extractions merit specific attention:

**F04 Ho Chi Minh City (Vietnam) active/reactive disambiguation.** The EVN invoice reported two metered quantities: 2,883,333 kWh of active energy and 437,582 kVArh of reactive energy. Reactive energy (kVArh) represents the component of power delivery that performs no useful work and carries no combustion-linked emission factor under GHG Protocol rules. The parser correctly extracted active energy only. Had this disambiguation failed and kVArh been included, gross emissions for the April invoice would have been overstated by approximately 15%.

**F06 Monterrey (Mexico) number format and multi-month period.** Total Gas Mexico invoices use European decimal notation (periods as thousands separators, commas as decimal points). The invoice quantity of 10.980,15 GJ was correctly parsed as 10,980.15 GJ. The invoice also explicitly provided a kWh equivalent (3,049,935 kWh); the parser correctly retained GJ as the primary quantity per extraction rules, preserving unit consistency with the GHG calculation chain.

**F01 Amsterdam (Netherlands) PPA treatment.** The Eneco invoice references REGO (Renewable Energy Guarantees of Origin) certificates backing Lumora's PPA. The parser captured this and flagged it as requiring dual Scope 2 treatment: location-based (Netherlands grid, 0.283 kgCO2e/kWh) and market-based (zero, given verified renewable certification). This distinction is correctly propagated through the emissions calculator.

---

## 2. Emissions Calculator

### Methodology

The emissions calculator applies GHG Protocol Corporate Standard emission factors to the parser-extracted quantities. Three fuel chains are covered:

- **Electricity (Scope 2):** IEA 2023 country grid factors (location-based); verified renewable energy certificates where applicable (market-based).
- **Natural gas (Scope 1):** IPCC AR6 WG III Annex II, 0.202 kgCO2e/kWh gross calorific value basis. Unit conversions: m³ to kWh using 10.55 kWh/m³ (GTS Groningen quality gas standard); GJ to kWh using 277.778 kWh/GJ.
- **Diesel (Scope 1):** DEFRA 2023 GHG Conversion Factors, 2.68 kgCO2e/litre (non-road diesel, forklift fleet).

### Results — Invoice Batch

| Facility | Energy Type | Quantity | Scope 1 (tCO2e) | S2 Location (tCO2e) | S2 Market (tCO2e) |
|---|---|---|---|---|---|
| F01 Amsterdam HQ | Electricity | 310,450 kWh | - | 87.86 | 0.00 |
| F02 Eindhoven Mfg | Diesel | 12,400 L | 33.23 | - | - |
| F02 Eindhoven Mfg | Natural gas | 172,510 m3 | 367.64 | - | - |
| F04 HCMC Mfg | Electricity | 2,883,333 kWh | - | 1,758.83 | 1,758.83 |
| F06 Monterrey Mfg | Natural gas | 10,980.15 GJ | 616.11 | - | - |
| **Invoice batch total** | | | **1,016.98** | **1,846.69** | **1,758.83** |

F01's market-based Scope 2 is correctly zero: the REGO-backed PPA eliminates attributed emissions under the market-based method. F04's market-based figure equals its location-based figure because Lumora has not procured renewable electricity in Vietnam; the HCMC facility is the portfolio's largest unmitigated Scope 2 source.

The F06 Monterrey figure (616.11 tCO2e Scope 1) covers only January-February 2023 and is substantially affected by the data anomaly described in Section 3.

---

## 3. Inventory Reconciliation

### Methodology

The reconciliation step compares parser-derived emission figures against the corresponding entries in Lumora's manual FY2023 GHG inventory. Because the inventory is structured by quarter and the invoice periods span monthly, quarterly, and bi-monthly windows, inventory values are prorated by day-overlap fraction before comparison. Variance thresholds: WARNING at >5%, ERROR at >15%.

### Results

| Facility | Energy | Invoice Period | Parser (tCO2e) | Inventory Prorated (tCO2e) | Variance | Flag |
|---|---|---|---|---|---|---|
| F01 Amsterdam HQ | Electricity | Jan 2023 | 87.86 | 30.22 | +190.7% | RECONCILIATION_ERROR |
| F02 Eindhoven Mfg | Diesel | Q1 2023 | 33.23 | 33.23 | 0.0% | RECONCILED |
| F02 Eindhoven Mfg | Natural gas | Q1 2023 | 367.64 | 367.64 | 0.0% | RECONCILED |
| F04 HCMC Mfg | Electricity | Apr 2023 | 1,758.83 | 1,739.51 | +1.1% | RECONCILED |
| F06 Monterrey Mfg | Natural gas | Jan-Feb 2023 | 616.11 | 206.58 | +198.2% | RECONCILIATION_ERROR |

Three of five records reconcile within tolerance. The two errors require investigation prior to base year finalisation.

**F01 Amsterdam HQ -- +190.7% error.** The January 2023 invoice records 310,450 kWh (310.5 MWh) of electricity consumption. The inventory records Q1 2023 electricity consumption for F01 as 310 MWh. These figures are near-identical, despite the invoice covering a single month (31 days) and the inventory period spanning a full quarter (90 days). The reconciliation system correctly prorates the quarterly inventory figure to the 31-day invoice window, yielding 30.22 tCO2e against the invoice-derived 87.86 tCO2e.

The most probable explanation is a data entry error in the inventory: the Q1 field was populated with a single-month figure rather than a quarterly aggregate. If correct, F01's actual Q1 consumption is approximately 930 MWh (three months at approximately 310 MWh each), not 310 MWh — roughly three times the reported value. This would increase F01's Scope 2 location-based annual total from 1,195 MWh (as reported) to approximately 3,500 MWh and its Scope 1 (natural gas) proportionally. **Resolution required before base year lock.**

**F06 Monterrey Mfg -- +198.2% error.** The January-February 2023 invoice records 10,980.15 GJ of natural gas consumption, equivalent to approximately 3,050 MWh. The inventory records Q1 2023 natural gas consumption for F06 as 1,560 MWh and Q2 as 1,490 MWh. The invoice figure for two months alone (3,050 MWh) exceeds the inventory total for the entire first half of the year (1,560 + 1,490 = 3,050 MWh).

This is structurally identical to the F01 anomaly: the inventory Q1 and Q2 values appear to represent monthly data entered in quarterly columns. If the actual quarterly natural gas consumption is approximately 4,590 MWh (three times 1,530 MWh monthly average), the annualised Scope 1 natural gas emissions for F06 would be substantially higher than the inventory implies -- compounding the existing DATA GAP on Q3 and Q4 noted in the data quality memo. **Resolution required before base year lock.**

---

## 4. Full FY2023 GHG Inventory

### Scope 1 and 2 -- Operational Emissions

Lumora operates nine facilities across seven countries. The table below summarises the FY2023 inventory under both the location-based and market-based Scope 2 methods.

| Facility | Country | Scope 1 (tCO2e) | S2 Location (tCO2e) | S2 Market (tCO2e) | Notes |
|---|---|---|---|---|---|
| F01 Amsterdam HQ | Netherlands | 116.4 | 338.2 | 0.0 | REGO-backed PPA |
| F02 Eindhoven Mfg | Netherlands | 1,556.2 | 5,411.0 | 0.0 | REGO-backed PPA |
| F03 Berlin Office | Germany | 76.2 | 267.9 | 0.0 | Green tariff certificate |
| F04 HCMC Mfg | Vietnam | 1,822.0 | 21,636.7 | 21,636.7 | No renewable procurement |
| F05 Penang Mfg | Malaysia | 1,579.6 | 17,795.7 | 17,795.7 | No renewable procurement |
| F06 Monterrey Mfg | Mexico | DATA GAP | 9,348.3 | 9,348.3 | Q3/Q4 metering failure; see Section 3 |
| F07 Austin R&D | USA | 164.6 | 951.5 | 951.5 | No renewable procurement |
| F08 Chicago Dist | USA | 152.7 | 621.5 | 621.5 | Annualised from 9 months (undisclosed) |
| F09 Singapore HQ | Singapore | 35.9 | 458.6 | 458.6 | No renewable procurement |
| **Total** | | **5,503.6** | **56,829.4** | **50,812.3** | |

Three facilities (F01, F02, F03) have reduced Scope 2 market-based emissions to zero through renewable energy procurement, avoiding **6,017.1 tCO2e** relative to the location-based method. This represents the portfolio's current renewable energy achievement and demonstrates the materiality of expanding procurement to the five remaining facilities, particularly F04 and F05 which together account for 77.3% of total Scope 2 market-based emissions.

Under the market-based method, F04 Ho Chi Minh City (23,458.7 tCO2e combined Scope 1+2) and F05 Penang (19,375.3 tCO2e) are the two largest operational emitters, driven by Vietnam and Malaysia grid emission factors of 0.610 and 0.585 kgCO2e/kWh respectively -- among the highest in the portfolio.

### Scope 3 -- Value Chain Emissions

| Category | tCO2e | % of S3 | Method | Data Quality |
|---|---|---|---|---|
| Cat 1: Purchased goods & services | 384,400 | 55.7% | Spend-based (EXIOBASE) | Low |
| Cat 3: Fuel & energy related activities | 4,280 | 0.6% | Calculated from S1+S2 | High |
| Cat 4: Upstream transport & distribution | 69,290 | 10.0% | Freight spend-based (GLEC) | Medium |
| Cat 11: Use of sold products | 198,400 | 28.8% | Sales-volume / global avg intensity | Low |
| Cat 12: End-of-life treatment | 33,600 | 4.9% | Sales-volume / e-waste EF | Low |
| **Total Scope 3** | **689,970** | **100%** | | |

Scope 3 constitutes 92.5% of Lumora's total GHG footprint. Category 1 alone (384,400 tCO2e) represents 51.5% of total Scope 1+2+3. The dominance of upstream supply chain and product use-phase emissions is characteristic of consumer electronics manufacturers and means Lumora's net-zero pathway is structurally dependent on supplier engagement and product efficiency improvement rather than operational energy management alone.

### Data Quality Assessment

The inventory contains several quality issues with material implications for base year integrity:

**F06 Monterrey -- Scope 1 data gap.** Q3 and Q4 natural gas consumption is absent due to a reported metering failure. In conjunction with the reconciliation anomaly in Section 3, the reported Q1 and Q2 inventory values are also likely to be monthly rather than quarterly figures. Until verified, F06 Scope 1 is not suitable for use in SBTi target-setting calculations.

**F04 Ho Chi Minh City -- Medium confidence.** Both Scope 1 natural gas and Scope 2 electricity data carry Medium confidence ratings due to unverified VND currency conversion and questions over meter reading methodology. F04 is the portfolio's largest emitter (23,458.7 tCO2e) and the largest single contributor to Scope 1+2 market-based emissions. A data quality gap at this facility creates material uncertainty in the inventory total.

**F08 Chicago Distribution -- Undisclosed annualisation.** Lumora acquired the Chicago facility in March 2023. The FY2023 inventory records what appears to be a full-year figure, but the annualisation methodology (extrapolation of 9-month actuals) is not documented. This is both a data quality issue and a boundary-setting question: GHG Protocol's base year stability provisions require that acquisitions be reflected consistently.

**F03 Berlin Office -- Landlord-provided data.** Q2 natural gas data was estimated by the building landlord. For leased assets, GHG Protocol permits the use of supplier-provided data but recommends independent verification for material emissions sources.

**Scope 3 Category 1 -- Spend-based estimation.** At 384,400 tCO2e (51.5% of total), Cat 1 is the single largest source and the weakest on data quality. EXIOBASE sector-average spend-based factors do not reflect Lumora's actual supplier energy mix or procurement geography. The confidence interval on this figure could plausibly span ±50% given sector heterogeneity. No SBTi-compliant third-party verification programme will accept spend-based estimation at this scale without a supplier data collection programme.

**Scope 3 Category 11 -- Global average intensity.** Cat 11 (198,400 tCO2e) assumes a uniform energy intensity across all product lines and a global average grid factor. Both assumptions introduce significant uncertainty. The data quality memo recommends product-level energy measurement for Lumora's top three SKUs and sales-weighted regional grid factors as a near-term improvement.

---

## 5. SBTi Gap Analysis

### Target Framework

Lumora's SBTi target architecture applies two methodologies in combination:

- **Cross-sector absolute contraction method** for Scope 1+2 and Scope 3 categories 1, 3, 4, and 12.
- **ICT sector approach** (SBTi ICT Sector Guidance, developed with GeSI) for Scope 3 Category 11, which models physical decarbonisation levers rather than a uniform absolute reduction rate.

The Scope 3 near-term target is mandatory: at 92.5% of total emissions, Scope 3 exceeds the SBTi 40% threshold, which triggers a required near-term Scope 3 target.

### Near-Term Targets (2030)

| Component | 2023 Base | 2030 Target | Reduction | Method |
|---|---|---|---|---|
| Scope 1+2 | 56,315.9 | 32,663.2 | -42% (23,652.7 tCO2e) | Cross-sector absolute contraction |
| Scope 3 Cat 11 | 198,400.0 | 118,048.0 | -40.5% (80,352.0 tCO2e) | ICT sector approach |
| Scope 3 other | 491,570.0 | 368,677.5 | -25% (122,892.5 tCO2e) | Cross-sector absolute contraction |
| **Total** | **746,285.9** | **519,388.7** | **-30.4% (226,897.2 tCO2e)** | |

**Annual reduction required (2024-2030): 32,413.9 tCO2e per year.**

### Long-Term Targets (2050)

Lumora's 2050 net-zero target requires a 90% absolute reduction from the 2023 base year across all scopes:

- **2050 target:** 74,628.6 tCO2e
- **Residual emissions:** 74,628.6 tCO2e, to be neutralised through carbon dioxide removal (CDR) -- not carbon market offsets, which do not satisfy the SBTi Net-Zero Standard residual requirement.
- **Annual reduction required (2031-2050): 22,238.0 tCO2e per year.**

### ICT Sector Approach -- Category 11

Category 11 was modelled under the SBTi ICT Sector Guidance rather than flat absolute contraction for the following reasons.

Consumer electronics use-phase emissions are governed by two physical parameters: (1) the energy consumed by the device over its lifetime, which is a function of product design; and (2) the carbon intensity of the electricity grid on which that device operates, which is outside Lumora's direct control but is declining across all major markets. Applying a flat 25% absolute reduction rate to Cat 11 would not distinguish between these mechanisms, obscure the product design lever available to Lumora's engineering teams, and fail to reflect the genuine trajectory of grid decarbonisation. The ICT sector approach makes both levers explicit and auditable.

The two components modelled are:

- **Product energy intensity improvement (-30% by 2030):** Based on IEA efficiency trends for consumer electronics, including standby power reductions mandated under the EU Ecodesign Regulation, display panel efficiency improvements, and component-level advances reflected in industry roadmaps (ENERGY STAR, EU Lot studies). This 30% improvement target should be translated into a product-level energy intensity metric (kWh per device-year) embedded in Lumora's product roadmap and tracked annually.

- **Grid decarbonisation contribution (-15% by 2030):** Based on projected improvement in sales-weighted average grid emission factors across Lumora's key product markets as renewable capacity expands. This figure is an approximation; a more robust analysis would use IEA country-level 2030 grid projections weighted by Lumora's sales geography.

The two effects are applied multiplicatively -- `1 - (1 - 0.30) x (1 - 0.15) = 40.5% combined reduction` -- because they act on different components of the same emission equation (device power draw versus grid emission factor). The resulting 2030 Cat 11 target of 118,048 tCO2e represents a more ambitious reduction than the 25% cross-sector floor would require (148,792 tCO2e at 25%).

**Verification requirement:** Lumora must formally verify ICT sector guidance applicability with SBTi before submitting targets. The guidance applies to companies classified under ISIC Rev.4 division 26 (manufacture of computer, electronic and optical products). As a consumer electronics manufacturer, Lumora is the expected primary candidate for this classification, but SBTi conducts a sector review at commitment letter stage. If SBTi assigns a different sector pathway, the Cat 11 trajectory and aggregate near-term target require revision. This analysis is directional until SBTi sector classification is confirmed.

### Key Abatement Priorities

**Priority 1 -- RE100 expansion (Scope 2 market-based).** Scope 2 market-based (50,812.3 tCO2e) represents 90.2% of Scope 1+2 and the fastest, lowest-cost near-term abatement pathway. F01, F02, and F03 have already demonstrated the mechanism works (combined renewable benefit: 6,017.1 tCO2e). Extending PPAs or utility green tariffs to F04 (21,636.7 tCO2e), F05 (17,795.7 tCO2e), F06 (9,348.3 tCO2e), and the three smaller sites would close the 42% Scope 1+2 target without capital expenditure on generation assets.

**Priority 2 -- Supplier data and engagement (Scope 3 Cat 1).** Category 1 at 384,400 tCO2e is the inventory's dominant emission source and its weakest data point. A 25% absolute reduction by 2030 requires 96,100 tCO2e of supplier-side decarbonisation over seven years. This is not achievable through procurement policy alone; it requires Lumora to establish primary emissions data collection from its top 20 suppliers (estimated to represent approximately 80% of category emissions) and incorporate supplier emissions performance into procurement criteria.

**Priority 3 -- Product energy intensity roadmap (Scope 3 Cat 11).** The ICT sector pathway requires measurable, verifiable product-level energy intensity improvement. Lumora's product development function should establish an energy intensity target (kWh per device-year) for each major product line and track it against the -30% trajectory. Without this, the Cat 11 2030 target will fail SBTi third-party verification.

**Priority 4 -- Scope 1 data resolution (F06 and F03).** The F06 Monterrey data gap and the F01/F06 reconciliation anomalies must be resolved before the FY2023 inventory is used as a SBTi base year. An incorrect base year cannot be corrected after target submission without triggering a full base year recalculation review.

---

## 6. Recommended Actions Before Base Year Lock

| Priority | Action | Owner | Deadline |
|---|---|---|---|
| 1 | Verify F01 Amsterdam Q1-Q4 electricity consumption against meter readings -- confirm whether inventory quarterly figures are monthly actuals | Facilities / Finance | Pre-disclosure |
| 2 | Verify F06 Monterrey Q1/Q2 natural gas consumption -- confirm whether inventory values are monthly or quarterly; recover Q3/Q4 from supplier records | Facilities / EHS | Pre-disclosure |
| 3 | Investigate F04 HCMC metering methodology and VND conversion approach; obtain independent meter reading confirmation | Regional EHS | Pre-disclosure |
| 4 | Document F08 Chicago annualisation methodology; confirm GHG Protocol boundary treatment for mid-year acquisition | Finance / EHS | Pre-disclosure |
| 5 | Launch supplier data collection for Scope 3 Cat 1 -- prioritise top 20 suppliers by spend | Procurement | 2024 Q3 |
| 6 | Commission product-level energy measurement for top 3 SKUs to underpin Cat 11 ICT pathway | Product / Engineering | 2024 Q4 |
| 7 | Engage SBTi to confirm sector classification (ISIC division 26) and validate ICT sector approach eligibility before target submission | Sustainability | 2024 Q3 |

---

## Appendix: Step 2 Output Files

| File | Description |
|---|---|
| `receipt-parser/parsed-invoices.csv` | Structured extraction output from 5 source invoices |
| `receipt-parser/parser.py` | RAG parser source code (Anthropic Claude API + CLI fallback) |
| `calculated-emissions.csv` | GHG Protocol emission calculations per invoice record |
| `calculate-emissions.py` | Emissions calculator + inventory reconciliation source code |
| `reconciliation-report.csv` | Detailed reconciliation results with variance flags |
| `lumora-ghg-inventory.csv` | Full FY2023 GHG inventory (Scope 1+2, 9 facilities) |
| `lumora-scope3.csv` | Scope 3 inventory (5 reported categories) |
| `lumora-data-quality-memo.md` | Detailed data quality findings and recommendations |
| `sbti-targets.csv` | Year-by-year SBTi reduction pathway (2023-2050) |
| `sbti-gap-summary.md` | SBTi gap analysis with ICT sector methodology narrative |
| `sbti-gap-analysis.py` | SBTi gap analysis source code |

---

*This memo was prepared as part of an AI-augmented climate risk consulting portfolio. All inventory data relates to the simulated client Lumora Technologies B.V. Methodology follows GHG Protocol Corporate Standard, SBTi Corporate Net-Zero Standard v1.2, and SBTi ICT Sector Guidance (GeSI).*
