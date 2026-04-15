# GHG Inventory Data Quality Memo
## Lumora Technologies B.V. | FY2023 Emissions Inventory

**Prepared by:** Taylor Black, Senior Sustainability & Climate Risk Professional
**Date:** April 2026
**Scope:** FY2023 Scope 1, 2, and Scope 3 (reported categories)
**Framework:** GHG Protocol Corporate Standard; CSRD ESRS E1

---

## Executive Summary

Lumora Technologies' FY2023 GHG inventory covers nine facilities across seven countries, reporting Scope 1, Scope 2 (location-based and market-based), and five Scope 3 categories. The total reported footprint on a market-based basis is approximately **746,300 tCO2e**, of which Scope 3 accounts for **92.5%** (689,970 tCO2e).

The inventory demonstrates strong data quality for the majority of European operations and reflects correct GHG Protocol treatment of Scope 2 market-based reporting, including verified zero-emission factors for the three facilities covered by PPAs and green tariffs. However, five material data quality issues were identified that must be resolved before this inventory can support CSRD ESRS E1 disclosure or SBTi target-setting:

1. **F06 Monterrey Scope 1 gap** — natural gas data is absent for Q3 and Q4 2023, leaving an estimated 616+ tCO2e unreported and violating the GHG Protocol completeness principle.
2. **F04 Ho Chi Minh City verification gap** — the largest emitting facility in the portfolio (~23,459 tCO2e Scope 1+2) carries Medium confidence due to unverified VND-denominated invoice data.
3. **F08 Chicago annualization not disclosed** — a mid-year acquisition has been annualized without disclosure, violating the GHG Protocol transparency principle.
4. **Scope 3 Category 1 low confidence** — 384,400 tCO2e estimated via spend-based method with no supplier-reported primary data; this is the single largest emissions source in the inventory (51.5% of total).
5. **Scope 3 Category 11 low confidence** — 198,400 tCO2e estimated using global average product energy intensity; product-specific measurements are absent.

Ten of 15 Scope 3 categories have not been assessed. A materiality screening of unassessed categories is required for CSRD compliance.

The inventory is not ready for external assurance or regulatory disclosure in its current form. With the corrective actions outlined in this memo, it can be made compliant with CSRD ESRS E1 requirements for the FY2025 reporting cycle.

---

## Methodology

This data quality audit was conducted against the following standards:

- **GHG Protocol Corporate Standard** (World Resources Institute / WBCSD, revised edition) — primary accounting framework
- **CSRD ESRS E1** — EU regulatory disclosure requirements applicable to Lumora as an EU-headquartered entity above the CSRD threshold
- **IPCC AR6** — emission factors for natural gas combustion (0.202 kgCO2e/kWh)
- **IEA Electricity Emission Factors 2023** — country-level grid emission factors
- **EPA eGRID 2023** — US regional grid emission factors
- **DEFRA 2023** — diesel combustion emission factors
- **EXIOBASE 3.8** — spend-based Scope 3 emission factors (Category 1)
- **GLEC Framework v2** — freight emission factors (Category 4)

Each line item in the inventory was assessed against a three-tier confidence scoring system:

| Tier | Label | Definition |
|------|-------|------------|
| 1 | High | Primary metered or invoice data; verified emission factor from named source |
| 2 | Medium | Secondary or estimated activity data; or unverified primary data with known limitations |
| 3 | Low | Spend-based or sales-volume proxy; significant assumptions; data gaps |

Emission factor sources were verified against the named references. Arithmetic was checked for all reported calculations. Reported totals were reconciled against facility-level inputs.

---

## Scope 1 and Scope 2 Findings

### Reported Totals

| Scope | Basis | Reported Emissions (tCO2e) | Notes |
|-------|-------|---------------------------|-------|
| Scope 1 | All sources | 5,503.6 | Excludes F06 Monterrey (data gap) |
| Scope 2 | Location-based | 56,829.4 | All nine facilities |
| Scope 2 | Market-based | 50,812.3 | Net of European PPA/green tariff RECs |
| **Scope 1+2** | **Market-based** | **56,315.9** | **Excludes F06 Scope 1 gap** |

The market-based Scope 2 benefit from European renewable energy procurement (F01, F02, F03) is **6,017.1 tCO2e**, representing a 10.6% reduction against the location-based figure for Scope 2 alone. All three European facilities have verified renewable energy certificates (REGOs and green tariff confirmation), and the zero emission factor application is correctly supported.

### Finding 1 — F06 Monterrey: Scope 1 Data Gap (CRITICAL)

**Confidence: Low | GHG Protocol issue: Completeness**

Monterrey Manufacturing's natural gas consumption for Q3 and Q4 2023 is absent due to a metering system failure. Only Q1 (1,560 MWh) and Q2 (1,490 MWh) data are available. No gross emissions figure has been calculated for this facility's Scope 1 natural gas, and no gap disclosure or estimation methodology has been applied.

H1 calculable emissions: 3,050 MWh × 0.202 kgCO2e/kWh = **616.1 tCO2e** (unreported)

Using H1 consumption as a proxy for H2, full-year Scope 1 natural gas for F06 is estimated at approximately **1,232 tCO2e**. The inventory as reported understates Scope 1 by at least 616 tCO2e and potentially by up to 1,232 tCO2e.

**Required action:** Obtain Q3/Q4 natural gas data from the utility provider, alternative invoices, or production-based estimation using H1 consumption per unit of output. Apply and disclose the estimation methodology. Do not leave the gap unaddressed in any CSRD submission.

### Finding 2 — F04 Ho Chi Minh City: Unverified Activity Data (HIGH)

**Confidence: Medium | GHG Protocol issue: Accuracy**

Ho Chi Minh City Manufacturing is Lumora's single largest emitting facility, contributing **23,458.7 tCO2e** on a Scope 1+2 market-based basis (41.7% of total Scope 1+2). Both the Scope 1 natural gas figure (1,822.0 tCO2e) and the Scope 2 electricity figure (21,636.7 tCO2e) carry Medium confidence because the underlying invoice data is denominated in Vietnamese Dong (VND) and the currency conversion and unit extraction have not been independently verified.

A unit conversion error or currency extraction error at this facility would have a material impact on the total Scope 1+2 inventory. A 5% error in F04 activity data translates to approximately 1,173 tCO2e — larger than the entire Scope 1 footprint of F07 or F08.

**Required action:** Independently verify F04 energy consumption data by reconciling VND-denominated invoices against metered consumption records. Engage the in-country facilities team or a local third-party verifier to confirm unit extraction. Upgrade confidence rating to High before any external assurance engagement.

### Finding 3 — F08 Chicago Distribution: Undisclosed Annualization (HIGH)

**Confidence: Medium | GHG Protocol issue: Transparency**

Chicago Distribution was acquired in March 2023. Only nine months of consumption data are available. The inventory has annualized both Scope 1 (756 MWh → 152.7 tCO2e) and Scope 2 electricity (1,610 MWh → 621.5 tCO2e) without disclosing the annualization methodology or flagging the partial-year basis to the reader.

The GHG Protocol Corporate Standard requires disclosure of the basis for partial-year data and any estimation applied. Annualizing without disclosure overstates the facility's contribution and misrepresents the boundary.

**Required action:** Add an explicit disclosure note to the inventory stating that F08 data covers March–December 2023 (nine months), annualized using a pro-rata factor of 12/9. Alternatively, report the nine-month actuals and note the partial-year boundary. Either approach is acceptable under the GHG Protocol; the absence of any disclosure is not.

### Finding 4 — F03 Berlin and F07 Austin: Landlord-Provided Data (MEDIUM)

**Confidence: Medium**

Berlin Office (F03) and Austin R&D (F07) both rely on landlord-provided or sub-metered estimates for Scope 1 natural gas, rather than direct metering. F03 also has an estimated Q2 value. Combined affected Scope 1 emissions: **240.8 tCO2e** (F03: 76.2 tCO2e; F07: 164.6 tCO2e).

This is a known limitation of leased premises and is not a GHG Protocol violation if disclosed. However, CSRD ESRS E1 requires entities to describe data collection methodologies and known limitations. Landlord-provided data without independent verification is unlikely to satisfy third-party assurance requirements.

**Required action:** For F03 and F07, document the landlord data collection process and any contractual data access provisions. Where lease renewals are due, negotiate direct metering access or sub-meter installation. Flag the limitation explicitly in the inventory methodology notes.

### Scope 2 Market-Based Treatment Assessment

The market-based Scope 2 treatment is correctly applied across all facilities:

- F01 (Amsterdam), F02 (Eindhoven): REGO-backed PPAs with verified certificates → zero emission factor correctly applied
- F03 (Berlin): Utility-verified green tariff → zero emission factor correctly applied
- F04 (HCMC), F05 (Penang), F06 (Monterrey), F07 (Austin), F08 (Chicago), F09 (Singapore): No renewable procurement → market-based factor equals location-based factor; correctly reported

The renewable energy procurement gap is notable in the context of Lumora's RE100 commitment. Six of nine facilities — representing approximately 84.7% of total electricity consumption (87,779 MWh of 103,579 MWh total) — have no renewable procurement in place as of FY2023.

---

## Scope 3 Findings

### Reported Totals

| Category | Method | Emissions (tCO2e) | Confidence | % of Reported Scope 3 |
|----------|--------|-------------------|------------|----------------------|
| Cat 1: Purchased goods & services | Spend-based | 384,400 | Low | 55.7% |
| Cat 3: Fuel & energy related activities | Calculated | 4,280 | High | 0.6% |
| Cat 4: Upstream transport & distribution | Spend-based | 69,290 | Medium | 10.0% |
| Cat 11: Use of sold products | Sales-volume based | 198,400 | Low | 28.8% |
| Cat 12: End of life treatment | Sales-volume based | 33,600 | Low | 4.9% |
| **Total reported** | | **689,970** | | **100%** |

Scope 3 represents **92.5%** of total reported GHG emissions (Scope 1+2+3 market-based: ~746,300 tCO2e). Three of the five reported categories carry Low confidence. Ten categories have not been assessed.

### Finding 5 — Category 1: Spend-Based Method, No Primary Supplier Data (CRITICAL)

**Confidence: Low | 384,400 tCO2e | 51.5% of total reported footprint**

Category 1 (purchased goods and services) is estimated using the EXIOBASE 3.8 electronics sector spend-based emission factor (0.31 tCO2e per USD 1,000 spend) applied to $1.24B in procurement spend. No supplier-reported primary data has been collected.

This is the largest single emissions source in Lumora's inventory — larger than all other Scope 3 categories combined, and nearly seven times the total Scope 1+2 footprint. The spend-based method is recognised as a starting point under the GHG Protocol Scope 3 Standard but carries significant uncertainty and does not reflect Lumora's actual supply chain energy mix.

Under CSRD ESRS E1, the spend-based approach is acceptable for the first reporting year but requires a disclosed pathway to higher-quality data. For SBTi purposes, Category 1 will be within scope of the Scope 3 near-term target if it exceeds 40% of total Scope 1+2+3 emissions — which it does (51.5%).

**Required action:** Launch a supplier data collection program targeting the top 20 suppliers by spend (estimated to represent approximately 80% of Category 1 emissions). Implement the GHG Protocol supplier engagement survey. In parallel, explore activity-based estimation (mass of materials procured × material-specific emission factors) for the top product categories (circuit boards, displays, enclosures) as a medium-confidence bridge.

### Finding 6 — Category 11: Global Average Energy Intensity (CRITICAL)

**Confidence: Low | 198,400 tCO2e | 26.6% of total reported footprint**

Use-phase emissions are estimated using a global average product energy intensity factor across all product types (laptops, tablets, keyboards, monitors, docking stations), assuming a four-year product lifetime and a global average grid factor. No product-specific energy measurements have been conducted.

This is a material weakness. Product energy consumption varies significantly across Lumora's SKU range — a gaming laptop and a wireless keyboard have fundamentally different use-phase profiles. Applying a uniform average to 4.2 million units sold understates uncertainty and is unlikely to be defensible under CSRD assurance.

Additionally, the global average grid factor does not reflect Lumora's actual sales geography (48% Europe, 31% North America, 21% Asia-Pacific), each of which has materially different average grid intensities.

**Required action:** Commission product-level energy consumption measurements for the top three SKUs by revenue. Apply sales-geography-weighted grid factors rather than a global average. This will both improve accuracy and better position Lumora for Ecodesign for Sustainable Products Regulation (ESPR) compliance, which requires product-level energy data.

### Finding 7 — Category 12: EU Average Recycling Rate Applied Globally (MEDIUM)

**Confidence: Low | 33,600 tCO2e**

End-of-life treatment emissions are estimated using the European Electronics Recycling Association average EU recycling rate (42%), applied uniformly to 4.2 million units sold globally. No data on actual end-of-life pathways in North American or Asia-Pacific markets has been collected.

EU and non-EU e-waste recycling rates differ materially. APAC average formal e-waste collection rates are substantially lower than the EU 42% figure; applying the EU rate to non-EU sales likely understates end-of-life emissions. Given Lumora's 52% non-EU sales share, this is a systematic bias.

**Required action:** Engage take-back scheme operators in North America and key APAC markets to obtain regional recovery rate data. Commission a targeted e-waste study for Vietnam and Malaysia markets, where Lumora has manufacturing presence and potentially higher brand visibility.

### Finding 8 — Category 4: Tonne-km Data Unavailable (MEDIUM)

**Confidence: Medium | 69,290 tCO2e**

Upstream transport is estimated using a freight spend-based factor (GLEC Framework v2, 0.82 tCO2e per USD 1,000 freight spend) applied to $84.5M in freight spend. Tonne-km data is not available for all lanes, and air freight proportion is estimated at 18% rather than measured.

The spend-based approach for freight is less accurate than a tonne-km/mode method, particularly given that air freight has approximately 50x the emission intensity of sea freight per tonne-km. Misestimating the air fraction by even a few percentage points creates meaningful error at this scale.

**Required action:** Collect tonne-km data from the top five logistics providers. Separate air, sea, and road freight by lane. This data is typically available from 3PL partners and should be contractually required going forward.

### Finding 9 — Scope 3 Category Coverage Gap (HIGH)

Ten of 15 Scope 3 categories have not been assessed:

| Unassessed Categories |
|----------------------|
| Cat 2: Capital goods |
| Cat 5: Waste generated in operations |
| Cat 6: Business travel |
| Cat 7: Employee commuting |
| Cat 8: Upstream leased assets |
| Cat 9: Downstream transportation |
| Cat 10: Processing of sold products |
| Cat 13: Downstream leased assets |
| Cat 14: Franchises |
| Cat 15: Investments |

For a consumer electronics manufacturer, Categories 2 (capital goods — manufacturing equipment purchases), 5 (waste — manufacturing scrap), 6 (business travel), and 7 (employee commuting) are typically material. Categories 14 and 15 are unlikely to be relevant given Lumora's business model.

CSRD ESRS E1 requires a disclosed methodology for determining which Scope 3 categories are included or excluded, with a materiality justification for exclusions. The current inventory lacks this disclosure.

**Required action:** Conduct a Scope 3 category screening using the GHG Protocol Scope 3 Standard relevance criteria. For each excluded category, document the materiality rationale. Estimate Categories 2, 5, 6, and 7 for the FY2025 reporting cycle.

---

## Prioritized Recommendations

| Priority | Finding | Action | Timeline |
|----------|---------|--------|----------|
| 1 | F06 Monterrey Scope 1 gap | Obtain Q3/Q4 data from utility or apply disclosed estimation methodology | Immediate — before any external disclosure |
| 2 | F04 HCMC data verification | Independently verify VND invoice data against metered records | Before FY2024 inventory close |
| 3 | F08 Chicago annualization | Add explicit partial-year disclosure to inventory methodology notes | Immediate — documentation fix |
| 4 | Cat 1 supplier data program | Launch supplier engagement targeting top 20 suppliers by spend | Begin Q3 2026; primary data target FY2026 inventory |
| 5 | Cat 11 product energy measurement | Commission product-level energy testing for top 3 SKUs | Begin Q3 2026; complete before FY2025 CSRD submission |
| 6 | Scope 3 category screening | Screen all 15 categories; document exclusion rationale | Before FY2025 CSRD submission |
| 7 | F03/F07 landlord data | Document methodology; negotiate metering access at lease renewal | Medium-term; flag in inventory methodology notes now |
| 8 | Cat 12 end-of-life data | Engage take-back scheme operators in NA and APAC | FY2026 inventory |
| 9 | Cat 4 tonne-km data | Collect tonne-km data from top 5 logistics providers | FY2025 inventory |
| 10 | RE100 procurement gap | Expand renewable electricity procurement to F04, F05, F06 as a minimum | Aligned with RE100 2030 target; initiate procurement now |

---

## Appendix

### Appendix A — Facility-Level Emissions Summary (FY2023)

| Facility | Country | Scope 1 (tCO2e) | Scope 2 Location (tCO2e) | Scope 2 Market (tCO2e) | S1+S2 Market (tCO2e) | Confidence |
|----------|---------|-----------------|--------------------------|------------------------|----------------------|------------|
| F01 Amsterdam HQ | Netherlands | 116.4 | 338.2 | 0.0 | 116.4 | High |
| F02 Eindhoven Mfg | Netherlands | 1,556.2 | 5,411.0 | 0.0 | 1,556.2 | High |
| F03 Berlin Office | Germany | 76.2 | 267.9 | 0.0 | 76.2 | Medium |
| F04 HCMC Mfg | Vietnam | 1,822.0 | 21,636.7 | 21,636.7 | 23,458.7 | Medium |
| F05 Penang Mfg | Malaysia | 1,579.6 | 17,795.7 | 17,795.7 | 19,375.3 | High |
| F06 Monterrey Mfg | Mexico | DATA GAP | 9,348.3 | 9,348.3 | DATA GAP | Low / High |
| F07 Austin R&D | USA | 164.6 | 951.5 | 951.5 | 1,116.1 | Medium |
| F08 Chicago Dist. | USA | 152.7 | 621.5 | 621.5 | 774.2 | Medium |
| F09 Singapore RHQ | Singapore | 35.9 | 458.6 | 458.6 | 494.5 | High |
| **Total** | | **5,503.6*** | **56,829.4** | **50,812.3** | **56,315.9*** | |

*Excludes F06 Scope 1 natural gas (data gap). F02 Scope 1 includes diesel: 132.7 tCO2e.*

### Appendix B — Scope 3 Category Register

| Category | Reported | Emissions (tCO2e) | Method | Confidence |
|----------|----------|-------------------|--------|------------|
| 1 — Purchased goods & services | Yes | 384,400 | Spend-based (EXIOBASE 3.8) | Low |
| 2 — Capital goods | No | Not assessed | — | — |
| 3 — Fuel & energy related | Yes | 4,280 | Calculated from S1+S2 | High |
| 4 — Upstream transport | Yes | 69,290 | Spend-based (GLEC v2) | Medium |
| 5 — Waste in operations | No | Not assessed | — | — |
| 6 — Business travel | No | Not assessed | — | — |
| 7 — Employee commuting | No | Not assessed | — | — |
| 8 — Upstream leased assets | No | Not assessed | — | — |
| 9 — Downstream transport | No | Not assessed | — | — |
| 10 — Processing of sold products | No | Not assessed | — | — |
| 11 — Use of sold products | Yes | 198,400 | Sales-volume / global avg EI | Low |
| 12 — End of life treatment | Yes | 33,600 | Sales-volume / EU avg rate | Low |
| 13 — Downstream leased assets | No | Not assessed | — | — |
| 14 — Franchises | No | Not assessed | — | — |
| 15 — Investments | No | Not assessed | — | — |
| **Total reported** | | **689,970** | | |

### Appendix C — Data Quality Flag Register

| Flag ID | Facility / Category | Issue | GHG Protocol Principle Affected | Severity |
|---------|---------------------|-------|----------------------------------|----------|
| DQ-01 | F06 Monterrey — Scope 1 | Q3/Q4 natural gas data missing; no estimation applied | Completeness | Critical |
| DQ-02 | F04 HCMC — Scope 1+2 | VND invoice data not independently verified | Accuracy | High |
| DQ-03 | F08 Chicago — Scope 1+2 | Partial-year annualization not disclosed | Transparency | High |
| DQ-04 | F03 Berlin — Scope 1 | Landlord-provided data; Q2 estimated | Accuracy | Medium |
| DQ-05 | F07 Austin — Scope 1 | Landlord-provided sub-metered estimate | Accuracy | Medium |
| DQ-06 | Scope 3 Cat 1 | Spend-based only; no primary supplier data | Accuracy / Completeness | Critical |
| DQ-07 | Scope 3 Cat 11 | Global average energy intensity; no product measurement | Accuracy | Critical |
| DQ-08 | Scope 3 Cat 12 | EU recycling rate applied to global sales | Accuracy | Medium |
| DQ-09 | Scope 3 Cat 4 | Air freight proportion estimated, not measured | Accuracy | Medium |
| DQ-10 | Scope 3 overall | 10 of 15 categories unassessed; no exclusion rationale | Completeness | High |

---

*Prepared as part of the AI-Augmented Sustainability & Climate Risk Portfolio | Taylor Black | github.com/taybeee/climate-portfolio*
