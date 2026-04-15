#!/usr/bin/env python3
"""
SBTi Gap Analysis -- Lumora Technologies B.V.
Framework: SBTi Corporate Net-Zero Standard v1.2 + ICT Sector Guidance
Base year:    FY2023
Near-term:    2030 (1.5 degrees C-aligned)
Long-term:    2050 (Net-Zero)

Methodology split:
  Scope 1+2          -- Cross-sector absolute contraction method (42% by 2030)
  Scope 3 Cat 11     -- ICT sector approach: product energy intensity improvement
                        + grid decarbonisation (SBTi ICT Sector Guidance / GeSI)
  Scope 3 other cats -- Cross-sector absolute contraction method (25% by 2030)
"""

from pathlib import Path
import csv

OUT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. Base-year emissions -- FY2023 verified inventory totals
# ---------------------------------------------------------------------------
BASE_YEAR = 2023

S1         = 5_503.6      # Scope 1 (tCO2e)
S2_MARKET  = 50_812.3     # Scope 2 market-based (tCO2e) -- used per SBTi
S12        = S1 + S2_MARKET                 # 56,315.9

# Scope 3 category breakdown (from lumora-scope3.csv)
S3_CAT11   = 198_400.0    # Cat 11: Use of sold products -- ICT sector method
S3_OTHER   = 491_570.0    # Cats 1, 3, 4, 12 -- cross-sector method
#   Cat 1  Purchased goods & services : 384,400
#   Cat 3  Fuel & energy related       :   4,280
#   Cat 4  Upstream transport          :  69,290
#   Cat 12 End-of-life treatment       :  33,600
S3_TOTAL   = S3_CAT11 + S3_OTHER            # 689,970.0

TOTAL_2023 = S12 + S3_TOTAL                 # 746,285.9

# ---------------------------------------------------------------------------
# 2. Near-term targets (2030) -- SBTi 1.5 degrees C pathway
# ---------------------------------------------------------------------------
NT_YEAR = 2030

# Scope 1+2: cross-sector absolute contraction, 42% reduction
NT_S12_RATE   = 0.42
NT_S12_TARGET = round(S12 * (1 - NT_S12_RATE), 1)          # 32,663.2

# Scope 3 Cat 11: ICT sector approach
#   Product energy intensity improvement by 2030: -30% (IEA consumer electronics trend)
#   Grid decarbonisation contribution by 2030:    -15%
#   Combined multiplicative effect: 1 - (1 - 0.30) * (1 - 0.15) = 40.5% reduction
CAT11_INTENSITY_IMPROVEMENT = 0.30
CAT11_GRID_DECARB            = 0.15
CAT11_COMBINED_RATE = 1 - (1 - CAT11_INTENSITY_IMPROVEMENT) * (1 - CAT11_GRID_DECARB)
NT_S3_CAT11_TARGET = round(S3_CAT11 * (1 - CAT11_COMBINED_RATE), 1)  # 118,048.0

# Scope 3 other categories: cross-sector absolute contraction, 25% reduction
NT_S3_RATE         = 0.25
NT_S3_OTHER_TARGET = round(S3_OTHER * (1 - NT_S3_RATE), 1)            # 368,677.5

NT_S3_TOTAL_TARGET = round(NT_S3_CAT11_TARGET + NT_S3_OTHER_TARGET, 1)
NT_TOTAL_TARGET    = round(NT_S12_TARGET + NT_S3_TOTAL_TARGET, 1)

# ---------------------------------------------------------------------------
# 3. Long-term targets (2050) -- SBTi Net-Zero Standard, 90% absolute reduction
#    Residual emissions (~10%) must be addressed via carbon dioxide removal (CDR),
#    not offsets. The 90% applies to total Scope 1+2+3 combined.
# ---------------------------------------------------------------------------
LT_YEAR   = 2050
LT_RATE   = 0.90

LT_S12_TARGET      = round(S12      * (1 - LT_RATE), 1)   # 5,631.6
LT_S3_CAT11_TARGET = round(S3_CAT11 * (1 - LT_RATE), 1)   # 19,840.0
LT_S3_OTHER_TARGET = round(S3_OTHER  * (1 - LT_RATE), 1)   # 49,157.0
LT_S3_TOTAL_TARGET = round(LT_S3_CAT11_TARGET + LT_S3_OTHER_TARGET, 1)
LT_TOTAL_TARGET    = round(TOTAL_2023 * (1 - LT_RATE), 1)  # 74,628.6
RESIDUAL_CDR       = LT_TOTAL_TARGET                        # required CDR by 2050

# ---------------------------------------------------------------------------
# 4. Annual linear reduction pathways
# ---------------------------------------------------------------------------
NT_YEARS = NT_YEAR - BASE_YEAR    # 7  (2024-2030)
LT_YEARS = LT_YEAR - NT_YEAR      # 20 (2031-2050)

# Near-term annual steps
STEP_S12_NT      = (S12      - NT_S12_TARGET)      / NT_YEARS
STEP_S3_C11_NT   = (S3_CAT11 - NT_S3_CAT11_TARGET) / NT_YEARS
STEP_S3_OTH_NT   = (S3_OTHER  - NT_S3_OTHER_TARGET)  / NT_YEARS

# Long-term annual steps (2030 values -> 2050 net-zero targets)
STEP_S12_LT      = (NT_S12_TARGET      - LT_S12_TARGET)      / LT_YEARS
STEP_S3_C11_LT   = (NT_S3_CAT11_TARGET - LT_S3_CAT11_TARGET) / LT_YEARS
STEP_S3_OTH_LT   = (NT_S3_OTHER_TARGET  - LT_S3_OTHER_TARGET)  / LT_YEARS


def _build_pathway() -> list[dict]:
    """Return year-by-year pathway from BASE_YEAR to LT_YEAR."""
    rows = []
    for year in range(BASE_YEAR, LT_YEAR + 1):
        if year == BASE_YEAR:
            s12      = S12
            s3_c11   = S3_CAT11
            s3_other = S3_OTHER
            ann_red  = 0.0
        elif year <= NT_YEAR:
            n        = year - BASE_YEAR
            s12      = S12      - n * STEP_S12_NT
            s3_c11   = S3_CAT11 - n * STEP_S3_C11_NT
            s3_other = S3_OTHER  - n * STEP_S3_OTH_NT
            ann_red  = STEP_S12_NT + STEP_S3_C11_NT + STEP_S3_OTH_NT
        else:
            n        = year - NT_YEAR
            s12      = NT_S12_TARGET      - n * STEP_S12_LT
            s3_c11   = NT_S3_CAT11_TARGET - n * STEP_S3_C11_LT
            s3_other = NT_S3_OTHER_TARGET  - n * STEP_S3_OTH_LT
            ann_red  = STEP_S12_LT + STEP_S3_C11_LT + STEP_S3_OTH_LT

        s3_total = s3_c11 + s3_other
        total    = s12 + s3_total
        rows.append({
            "year":                             year,
            "scope1_2_target_tCO2e":            round(s12,      1),
            "scope3_cat11_target_tCO2e":        round(s3_c11,   1),
            "scope3_other_target_tCO2e":        round(s3_other, 1),
            "scope3_total_target_tCO2e":        round(s3_total, 1),
            "total_target_tCO2e":               round(total,    1),
            "annual_reduction_required_tCO2e":  round(ann_red,  1),
        })
    return rows


def write_csv(pathway: list[dict]) -> None:
    out = OUT_DIR / "sbti-targets.csv"
    fields = list(pathway[0].keys())
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(pathway)
    print(f"Pathway written to: {out}  ({len(pathway)} rows)")


def write_summary_md() -> None:
    """Write consulting-grade markdown gap summary."""
    out = OUT_DIR / "sbti-gap-summary.md"

    # Derived figures for the narrative
    s12_reduction_abs    = round(S12      - NT_S12_TARGET,      1)
    c11_reduction_abs    = round(S3_CAT11 - NT_S3_CAT11_TARGET, 1)
    s3oth_reduction_abs  = round(S3_OTHER  - NT_S3_OTHER_TARGET,  1)
    s3_total_reduction   = round(S3_TOTAL  - NT_S3_TOTAL_TARGET,  1)
    total_2030_reduction = round(TOTAL_2023 - NT_TOTAL_TARGET,   1)
    total_2050_reduction = round(TOTAL_2023 - LT_TOTAL_TARGET,   1)

    ann_nt = round(STEP_S12_NT + STEP_S3_C11_NT + STEP_S3_OTH_NT, 1)
    ann_lt = round(STEP_S12_LT + STEP_S3_C11_LT + STEP_S3_OTH_LT, 1)

    s3_pct_of_total = round(S3_TOTAL / TOTAL_2023 * 100, 1)
    c11_pct_of_s3   = round(S3_CAT11 / S3_TOTAL   * 100, 1)
    c11_pct_of_tot  = round(S3_CAT11 / TOTAL_2023 * 100, 1)

    content = f"""\
# SBTi Gap Analysis: Lumora Technologies B.V.

**Framework:** SBTi Corporate Net-Zero Standard v1.2 + ICT Sector Guidance (GeSI)
**Base year:** FY2023
**Prepared by:** Taylor Black | Climate Risk & Sustainability

---

## Executive Summary

Lumora Technologies' FY2023 GHG inventory totals **{TOTAL_2023:,.1f} tCO2e**. Scope 3
accounts for {s3_pct_of_total}% of total emissions, exceeding the SBTi 40% threshold and
making near-term Scope 3 targets mandatory. Category 11 (use of sold products) represents
{c11_pct_of_tot}% of total emissions and qualifies for the SBTi ICT sector approach, which
models product energy intensity improvement and grid decarbonisation rather than applying
a flat absolute contraction rate.

To align with SBTi's 1.5 degrees C pathway, Lumora must reduce total emissions by
**{total_2030_reduction:,.1f} tCO2e ({round(total_2030_reduction/TOTAL_2023*100,1)}%)** by 2030, then continue to a
net-zero position of **{LT_TOTAL_TARGET:,.1f} tCO2e** by 2050, with residual emissions
addressed through carbon dioxide removal (CDR).

---

## 1. Base Year Emissions (FY2023)

| Component | tCO2e | % of Total |
|---|---|---|
| Scope 1 (stationary + mobile combustion) | {S1:,.1f} | {round(S1/TOTAL_2023*100,1)}% |
| Scope 2 market-based | {S2_MARKET:,.1f} | {round(S2_MARKET/TOTAL_2023*100,1)}% |
| **Scope 1+2** | **{S12:,.1f}** | **{round(S12/TOTAL_2023*100,1)}%** |
| Scope 3 Category 11 (use of sold products) | {S3_CAT11:,.1f} | {round(S3_CAT11/TOTAL_2023*100,1)}% |
| Scope 3 other categories (1, 3, 4, 12) | {S3_OTHER:,.1f} | {round(S3_OTHER/TOTAL_2023*100,1)}% |
| **Scope 3 total** | **{S3_TOTAL:,.1f}** | **{round(S3_TOTAL/TOTAL_2023*100,1)}%** |
| **Total Scope 1+2+3** | **{TOTAL_2023:,.1f}** | **100.0%** |

Scope 2 market-based figures reflect zero-carbon renewable electricity under Lumora's
current PPA arrangement for the Amsterdam headquarters. Scope 3 Cat 1 (384,400 tCO2e)
uses spend-based estimation; Cat 11 (198,400 tCO2e) uses global average energy intensity.
Both carry **Low** data quality ratings and are candidates for primary data improvement
prior to formal SBTi submission.

---

## 2. Target Framework

| Scope / Category | Method | Reduction Rate | Basis |
|---|---|---|---|
| Scope 1+2 | Cross-sector absolute contraction | 42% by 2030 | SBTi 1.5 degrees C pathway |
| Scope 3 Category 11 | ICT sector approach | 40.5% by 2030 | Energy intensity -30% x grid decarb -15% (multiplicative) |
| Scope 3 other (1, 3, 4, 12) | Cross-sector absolute contraction | 25% by 2030 | SBTi 1.5 degrees C pathway (mandatory; S3 > 40% of total) |
| All scopes (net-zero) | Absolute reduction | 90% by 2050 | SBTi Corporate Net-Zero Standard |
| Residual emissions | Carbon dioxide removal | {RESIDUAL_CDR:,.1f} tCO2e by 2050 | CDR only -- offsets do not qualify |

---

## 3. Near-Term Targets (2030)

| Component | Base Year (2023) | 2030 Target | Required Reduction | Reduction % |
|---|---|---|---|---|
| Scope 1+2 | {S12:,.1f} | {NT_S12_TARGET:,.1f} | {s12_reduction_abs:,.1f} | {round(NT_S12_RATE*100,1)}% |
| Scope 3 Cat 11 | {S3_CAT11:,.1f} | {NT_S3_CAT11_TARGET:,.1f} | {c11_reduction_abs:,.1f} | {round(CAT11_COMBINED_RATE*100,1)}% |
| Scope 3 other | {S3_OTHER:,.1f} | {NT_S3_OTHER_TARGET:,.1f} | {s3oth_reduction_abs:,.1f} | {round(NT_S3_RATE*100,1)}% |
| **Total** | **{TOTAL_2023:,.1f}** | **{NT_TOTAL_TARGET:,.1f}** | **{total_2030_reduction:,.1f}** | **{round(total_2030_reduction/TOTAL_2023*100,1)}%** |

Annual reduction required (2024-2030): **{ann_nt:,.1f} tCO2e/year**

---

## 4. Long-Term Targets (2050 -- Net Zero)

| Component | 2030 Target | 2050 Target | Additional Reduction (2030-2050) |
|---|---|---|---|
| Scope 1+2 | {NT_S12_TARGET:,.1f} | {LT_S12_TARGET:,.1f} | {round(NT_S12_TARGET-LT_S12_TARGET,1):,.1f} |
| Scope 3 Cat 11 | {NT_S3_CAT11_TARGET:,.1f} | {LT_S3_CAT11_TARGET:,.1f} | {round(NT_S3_CAT11_TARGET-LT_S3_CAT11_TARGET,1):,.1f} |
| Scope 3 other | {NT_S3_OTHER_TARGET:,.1f} | {LT_S3_OTHER_TARGET:,.1f} | {round(NT_S3_OTHER_TARGET-LT_S3_OTHER_TARGET,1):,.1f} |
| **Total** | **{NT_TOTAL_TARGET:,.1f}** | **{LT_TOTAL_TARGET:,.1f}** | **{round(NT_TOTAL_TARGET-LT_TOTAL_TARGET,1):,.1f}** |

Annual reduction required (2031-2050): **{ann_lt:,.1f} tCO2e/year**

Residual emissions of **{RESIDUAL_CDR:,.1f} tCO2e** in 2050 must be neutralised via
permanent carbon dioxide removal (e.g., BECCS, DACCS, enhanced weathering). Carbon
market offsets do not satisfy the SBTi Net-Zero Standard residual requirement.

---

## 5. Key Implications for Lumora

**Scope 2 is the fastest near-term lever.** Scope 2 market-based (50,812.3 tCO2e)
constitutes 90.2% of Scope 1+2. Expanding the existing Amsterdam PPA to cover all
electricity-consuming facilities (Eindhoven, Ho Chi Minh City, Monterrey, and others)
would deliver the majority of the 42% Scope 1+2 reduction without capital investment
in on-site generation.

**Category 1 spend-based data limits target credibility.** At 384,400 tCO2e (55.7% of
Scope 3), Category 1 is the single largest emissions source. The spend-based method
carries Low data quality and will not withstand SBTi third-party verification. Lumora
must launch a supplier data collection programme targeting its top 20 suppliers (estimated
80% of category emissions) before formal target submission.

**Category 11 ICT pathway is more ambitious than the cross-sector method for this
category.** The combined 40.5% reduction (energy intensity + grid decarbonisation) exceeds
the 25% cross-sector Scope 3 requirement. This reflects the genuine decarbonisation
lever available through product efficiency improvement -- Lumora's product roadmap should
incorporate measurable energy intensity targets (e.g., kWh per device-year) to underpin
this trajectory.

**Scope 3 data quality must improve before SBTi submission.** Two of five reported
categories carry Low confidence (Cat 1, Cat 11), and Cat 12 relies on estimated recycling
rates. The reconciliation analysis (see reconciliation-report.csv) identified additional
temporal inconsistencies in the FY2023 dataset. A structured data quality improvement
plan (see lumora-data-quality-memo.md) should be completed before base year is locked.

**Long-term CDR requirement is material.** The {RESIDUAL_CDR:,.1f} tCO2e residual by
2050 represents a significant CDR procurement obligation. Lumora should begin CDR market
scoping in the 2028-2032 timeframe to secure supply at scale.

---

## 6. Methodology Notes

### Cross-Sector Absolute Contraction Method
Applied to Scope 1+2 and Scope 3 categories 1, 3, 4, and 12. Under this method, the
company commits to an absolute percentage reduction from a fixed base year, regardless
of production or revenue growth. The 42% Scope 1+2 rate and 25% Scope 3 rate are the
minimum thresholds for SBTi 1.5 degrees C alignment per the Corporate Net-Zero Standard.

### ICT Sector Approach -- Category 11
Category 11 (use of sold products) was modelled using the SBTi ICT Sector Science-Based
Target Setting Guidance (developed in collaboration with GeSI, the Global e-Sustainability
Initiative). This approach is applicable to ICT companies where end-use product emissions
are driven by device energy intensity and the carbon intensity of the electricity grids
on which products are used -- both of which are expected to improve independently of
Lumora's own operations.

**How it differs from the cross-sector method:**
The cross-sector absolute contraction method requires a fixed percentage reduction from
the base year total, irrespective of the drivers of that emission. The ICT sector approach
instead models two independent physical levers:
- **Product energy intensity improvement** (-30% by 2030): reflects IEA efficiency trends
  for consumer electronics, including standby power reductions, display efficiency gains,
  and component-level improvements driven by industry roadmaps (e.g., ENERGY STAR,
  EU Ecodesign Regulation).
- **Grid decarbonisation** (-15% by 2030): reflects projected improvement in average
  global grid emission factors as renewable capacity expands, reducing the emissions
  intensity of electricity consumed by Lumora's products in use.

These two effects are applied multiplicatively: `1 - (1 - 0.30) * (1 - 0.15) = 40.5%`
combined reduction by 2030 -- more ambitious than the 25% cross-sector floor.

The ICT method requires product-level energy intensity data (kWh per device-year by
product line) and sales-weighted regional grid factors to be credible. Lumora's current
Cat 11 estimate uses a global average energy intensity (Low data quality); upgrading to
product-level measurements is a prerequisite for using this approach in a submitted target.

### Verification Flag
**Lumora must formally verify ICT sector guidance applicability with SBTi before
submitting targets.** The SBTi ICT Sector Guidance applies to companies with ISIC
Rev.4 codes in divisions 26 (manufacture of computer, electronic and optical products),
61 (telecommunications), and 62/63 (IT services). As a consumer electronics manufacturer,
Lumora likely qualifies under division 26, but SBTi conducts a sector classification
review at the time of commitment letter submission. If SBTi classifies Lumora under a
different sector pathway, the Cat 11 trajectory and overall near-term target will require
revision. This analysis should be treated as directional until SBTi classification is
confirmed.

---

## Appendix: Annual Reduction Pathway Summary

| Period | Scope 1+2 Annual Step | Cat 11 Annual Step | Other S3 Annual Step | Total Annual Step |
|---|---|---|---|---|
| 2024-2030 (near-term) | {round(STEP_S12_NT,1):,.1f} tCO2e/yr | {round(STEP_S3_C11_NT,1):,.1f} tCO2e/yr | {round(STEP_S3_OTH_NT,1):,.1f} tCO2e/yr | {ann_nt:,.1f} tCO2e/yr |
| 2031-2050 (long-term) | {round(STEP_S12_LT,1):,.1f} tCO2e/yr | {round(STEP_S3_C11_LT,1):,.1f} tCO2e/yr | {round(STEP_S3_OTH_LT,1):,.1f} tCO2e/yr | {ann_lt:,.1f} tCO2e/yr |

Full year-by-year pathway: `sbti-targets.csv`

---

*Prepared using SBTi Corporate Net-Zero Standard v1.2, SBTi ICT Sector Guidance (GeSI),
IEA World Energy Outlook 2023 efficiency projections, and Lumora's FY2023 GHG inventory.
This analysis is indicative and does not constitute an officially validated SBTi target.*
"""

    with open(out, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Summary written to:  {out}")


def print_console_summary() -> None:
    ann_nt = round(STEP_S12_NT + STEP_S3_C11_NT + STEP_S3_OTH_NT, 1)
    print()
    print("-" * 80)
    print("SBTi GAP ANALYSIS -- Lumora Technologies B.V.")
    print(f"Base year: FY{BASE_YEAR}  |  Framework: Corporate Net-Zero Standard v1.2 + ICT")
    print("-" * 80)
    print(f"  Base year total emissions  : {TOTAL_2023:>12,.1f} tCO2e")
    print(f"    Scope 1+2                : {S12:>12,.1f} tCO2e")
    print(f"    Scope 3 Cat 11 (ICT)     : {S3_CAT11:>12,.1f} tCO2e")
    print(f"    Scope 3 other            : {S3_OTHER:>12,.1f} tCO2e")
    print()
    print(f"  2030 near-term targets (1.5 degrees C)")
    print(f"    Scope 1+2  (-42%)        : {NT_S12_TARGET:>12,.1f} tCO2e")
    print(f"    Cat 11     (-40.5% ICT)  : {NT_S3_CAT11_TARGET:>12,.1f} tCO2e")
    print(f"    S3 other   (-25%)        : {NT_S3_OTHER_TARGET:>12,.1f} tCO2e")
    print(f"    Total 2030               : {NT_TOTAL_TARGET:>12,.1f} tCO2e")
    print(f"    Annual reduction needed  : {ann_nt:>12,.1f} tCO2e/yr")
    print()
    print(f"  2050 net-zero targets (-90%)")
    print(f"    Total 2050               : {LT_TOTAL_TARGET:>12,.1f} tCO2e")
    print(f"    Residual (CDR required)  : {RESIDUAL_CDR:>12,.1f} tCO2e")
    print("-" * 80)


def main() -> None:
    pathway = _build_pathway()
    write_csv(pathway)
    write_summary_md()
    print_console_summary()


if __name__ == "__main__":
    main()
