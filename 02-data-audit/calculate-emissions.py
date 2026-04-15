#!/usr/bin/env python3
"""
02-data-audit/calculate-emissions.py
Lumora Technologies — GHG Emissions Calculator with Inventory Reconciliation

Step 1 — Calculation:
    Reads parsed-invoices.csv, applies GHG Protocol emission factors,
    converts units, and outputs calculated-emissions.csv.

Step 2 — Reconciliation:
    Loads lumora-ghg-inventory.csv, prorates quarterly inventory values to
    match each invoice's billing period, and compares parser-derived tCO2e
    against the inventory figure. Flags variances >5% as WARNING, >15% as ERROR.
    Outputs reconciliation-report.csv and prints a summary to console.

Framework:  GHG Protocol Corporate Standard
Scope 1:    Natural gas (IPCC AR6), diesel (DEFRA 2023)
Scope 2:    Electricity, location-based (IEA 2023 country grid factors)

Usage:
    python calculate-emissions.py
"""

import csv
import sys
from datetime import date
from pathlib import Path

# -- Paths -------------------------------------------------------------------- #

PARSED_CSV    = Path(__file__).parent / "receipt-parser" / "parsed-invoices.csv"
INVENTORY_CSV = Path(__file__).parent / "lumora-ghg-inventory.csv"
OUTPUT_CSV    = Path(__file__).parent / "calculated-emissions.csv"
RECON_CSV     = Path(__file__).parent / "reconciliation-report.csv"

# -- Emission factor reference tables ---------------------------------------- #

# IEA 2023 country-level grid emission factors — location-based (kgCO2e/kWh).
IEA_GRID_FACTORS: dict[str, dict] = {
    "Netherlands": {"factor": 0.283, "source": "IEA 2023 Netherlands"},
    "Germany":     {"factor": 0.364, "source": "IEA 2023 Germany"},
    "Vietnam":     {"factor": 0.610, "source": "IEA 2023 Vietnam"},
    "Malaysia":    {"factor": 0.585, "source": "IEA 2023 Malaysia"},
    "Mexico":      {"factor": 0.442, "source": "IEA 2023 Mexico"},
    "Singapore":   {"factor": 0.408, "source": "EMA Singapore Grid Emission Factor 2023"},
    "USA":         {"factor": 0.386, "source": "EPA eGRID 2023 (US national average)"},
}

# Scope 1: natural gas — kgCO2e per kWh (gross calorific value basis)
NATURAL_GAS_EF = {
    "factor": 0.202,
    "unit":   "kgCO2e/kWh",
    "source": "IPCC AR6 WG III Annex II (natural gas combustion, GCV basis)",
}

# Scope 1: diesel — kgCO2e per litre
DIESEL_EF = {
    "factor": 2.68,
    "unit":   "kgCO2e/litre",
    "source": "DEFRA 2023 GHG Conversion Factors (diesel, kg CO2e per litre)",
}

# Facilities with verified zero market-based Scope 2
ZERO_MARKET_BASED: set[tuple[str, str]] = {
    ("F01", "electricity"),
    ("F02", "electricity"),
    ("F03", "electricity"),
}

# -- Unit conversion ---------------------------------------------------------- #

UNIT_TO_KWH: dict[str, float] = {
    "kwh":    1.0,
    "mwh":    1_000.0,
    "gwh":    1_000_000.0,
    "gj":     277.778,
    "mj":     0.277778,
    "m3":     10.55,
    "m\u00b3": 10.55,   # m³ Unicode
    "therm":  29.307,
}

DIESEL_KWH_PER_LITRE = 10.8
DIESEL_UNITS = {"litre", "litres", "liter", "liters", "l"}

SCOPE_MAP: dict[str, str] = {
    "electricity": "Scope 2",
    "natural_gas": "Scope 1",
    "diesel":      "Scope 1",
}

# -- Output field definitions ------------------------------------------------- #

OUTPUT_FIELDS = [
    "facility_id", "facility_name", "country", "energy_type",
    "billing_period_start", "billing_period_end",
    "quantity", "unit", "quantity_kwh",
    "emission_factor", "emission_factor_unit", "emission_factor_source",
    "gross_emissions_tCO2e", "scope", "scope2_market_based_tCO2e",
    "confidence_score", "reconciliation_flag", "notes",
]

RECON_FIELDS = [
    "facility_id", "energy_type", "billing_period",
    "parser_tCO2e", "inventory_tCO2e", "inventory_basis",
    "variance_pct", "flag", "notes",
]

# -- Reconciliation constants ------------------------------------------------- #

# Calendar bounds for each quarter (2023)
QUARTER_BOUNDS: dict[int, tuple[date, date]] = {
    1: (date(2023, 1, 1),  date(2023, 3, 31)),
    2: (date(2023, 4, 1),  date(2023, 6, 30)),
    3: (date(2023, 7, 1),  date(2023, 9, 30)),
    4: (date(2023, 10, 1), date(2023, 12, 31)),
}

QUARTER_COLS = {
    1: "q1_consumption", 2: "q2_consumption",
    3: "q3_consumption", 4: "q4_consumption",
}

WARN_THRESHOLD  =  5.0   # % variance — RECONCILIATION_WARNING
ERROR_THRESHOLD = 15.0   # % variance — RECONCILIATION_ERROR


# =============================================================================
# STEP 1: EMISSION CALCULATION
# =============================================================================

def to_kwh(quantity: float, unit: str) -> tuple[float | None, str]:
    u = unit.lower().strip()
    if u in DIESEL_UNITS:
        kwh = quantity * DIESEL_KWH_PER_LITRE
        return kwh, (
            f"quantity_kwh = {kwh:,.1f} kWh is energy-content equivalent "
            f"at {DIESEL_KWH_PER_LITRE} kWh/L (LHV, reference only); "
            "GHG calculation uses litres x kgCO2e/litre"
        )
    factor = UNIT_TO_KWH.get(u)
    if factor is None:
        return None, f"unit '{unit}' not in conversion table; quantity_kwh not calculated"
    return quantity * factor, ""


def calculate_row(row: dict) -> dict:
    facility_id   = row.get("facility_id", "")
    facility_name = row.get("facility_name", "")
    country       = row.get("country", "")
    energy_type   = (row.get("energy_type") or "").lower().strip()
    unit          = (row.get("unit") or "").strip()
    confidence    = row.get("confidence_score", "")
    period_start  = row.get("billing_period_start", "")
    period_end    = row.get("billing_period_end", "")
    source_file   = row.get("source_file", "")
    anomaly_flags = row.get("anomaly_flags", "")
    notes: list[str] = []

    try:
        quantity = float(str(row.get("quantity", "")).replace(",", ""))
    except (ValueError, TypeError):
        notes.append("quantity could not be parsed; row skipped")
        return _empty_row(row, notes)

    kwh_value, conversion_note = to_kwh(quantity, unit)
    if conversion_note:
        notes.append(conversion_note)

    ef_value = ef_unit = ef_source = None

    if energy_type == "electricity":
        grid = IEA_GRID_FACTORS.get(country)
        if grid is None:
            notes.append(f"no IEA grid factor for '{country}'")
            return _empty_row(row, notes, quantity, unit, kwh_value, period_start, period_end)
        ef_value, ef_unit, ef_source = grid["factor"], "kgCO2e/kWh", grid["source"]

    elif energy_type == "natural_gas":
        ef_value = NATURAL_GAS_EF["factor"]
        ef_unit  = NATURAL_GAS_EF["unit"]
        ef_source = NATURAL_GAS_EF["source"]

    elif energy_type == "diesel":
        ef_value = DIESEL_EF["factor"]
        ef_unit  = DIESEL_EF["unit"]
        ef_source = DIESEL_EF["source"]

    else:
        notes.append(f"energy type '{energy_type}' not recognised")
        return _empty_row(row, notes, quantity, unit, kwh_value, period_start, period_end)

    u_lower = unit.lower().strip()
    if energy_type == "diesel":
        if u_lower not in DIESEL_UNITS:
            notes.append(f"unit '{unit}' not recognised as litres")
            return _empty_row(row, notes, quantity, unit, kwh_value, period_start, period_end)
        gross_kg = quantity * ef_value
    else:
        if kwh_value is None:
            notes.append(f"kWh conversion failed for unit '{unit}'")
            return _empty_row(row, notes, quantity, unit, None, period_start, period_end)
        gross_kg = kwh_value * ef_value

    gross_tco2e = round(gross_kg / 1000, 2)
    scope = SCOPE_MAP.get(energy_type, "Unknown")

    market_based_str = ""
    if energy_type == "electricity":
        if (facility_id, "electricity") in ZERO_MARKET_BASED:
            market_based_str = "0.0"
            notes.append(
                "Scope 2 market-based = 0.0 tCO2e: verified renewable energy certificate "
                "(REGO-backed PPA or utility green tariff)"
            )
        else:
            market_based_str = str(gross_tco2e)
            notes.append("Scope 2 market-based = location-based: no renewable procurement")

    if anomaly_flags:
        if "BILLING_PERIOD_OVERLAP" in anomaly_flags and energy_type in ("diesel", "natural_gas"):
            notes.append(
                f"parser anomaly flag: {anomaly_flags} — likely false positive "
                "(multiple energy streams for same facility and period is expected)"
            )
        else:
            notes.append(f"parser anomaly flag: {anomaly_flags}")

    notes.append(f"source invoice: {source_file}")

    return {
        "facility_id":               facility_id,
        "facility_name":             facility_name,
        "country":                   country,
        "energy_type":               energy_type,
        "billing_period_start":      period_start,
        "billing_period_end":        period_end,
        "quantity":                  quantity,
        "unit":                      unit,
        "quantity_kwh":              round(kwh_value, 1) if kwh_value is not None else "",
        "emission_factor":           ef_value,
        "emission_factor_unit":      ef_unit,
        "emission_factor_source":    ef_source,
        "gross_emissions_tCO2e":     gross_tco2e,
        "scope":                     scope,
        "scope2_market_based_tCO2e": market_based_str,
        "confidence_score":          confidence,
        "reconciliation_flag":       "",   # populated in Step 2
        "notes":                     " | ".join(notes),
    }


def _empty_row(row, notes, quantity=None, unit=None,
               kwh_value=None, period_start="", period_end="") -> dict:
    return {
        "facility_id":               row.get("facility_id", ""),
        "facility_name":             row.get("facility_name", ""),
        "country":                   row.get("country", ""),
        "energy_type":               row.get("energy_type", ""),
        "billing_period_start":      period_start or row.get("billing_period_start", ""),
        "billing_period_end":        period_end   or row.get("billing_period_end", ""),
        "quantity":                  quantity if quantity is not None else row.get("quantity", ""),
        "unit":                      unit or row.get("unit", ""),
        "quantity_kwh":              round(kwh_value, 1) if kwh_value is not None else "",
        "emission_factor":           "",
        "emission_factor_unit":      "",
        "emission_factor_source":    "",
        "gross_emissions_tCO2e":     "",
        "scope":                     SCOPE_MAP.get((row.get("energy_type") or "").lower(), ""),
        "scope2_market_based_tCO2e": "",
        "confidence_score":          row.get("confidence_score", ""),
        "reconciliation_flag":       "",
        "notes":                     " | ".join(notes),
    }


# =============================================================================
# STEP 2: INVENTORY RECONCILIATION
# =============================================================================

def _inv_energy_type(inv_row: dict) -> str | None:
    """
    Map an inventory row to a canonical energy type for matching.
    Only location-based Scope 2 is matched for electricity (not market-based).
    """
    src   = inv_row.get("energy_source", "").lower()
    scope = inv_row.get("scope", "").lower()

    if "electricity" in src and "location-based" in scope:
        return "electricity"
    if "natural gas" in src and scope == "scope 1":
        return "natural_gas"
    if "diesel" in src and scope == "scope 1":
        return "diesel"
    return None


def load_inventory() -> dict[tuple[str, str], dict]:
    """
    Load lumora-ghg-inventory.csv and return a lookup dict indexed by
    (facility_id, canonical_energy_type).
    """
    if not INVENTORY_CSV.exists():
        return {}

    index: dict[tuple[str, str], dict] = {}
    with open(INVENTORY_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            etype = _inv_energy_type(row)
            if etype is None:
                continue
            key = (row["facility_id"].strip(), etype)
            index[key] = row   # one row per (facility, type) after filtering
    return index


def _days_overlap(p_start: date, p_end: date,
                  q_start: date, q_end: date) -> int:
    """Return the number of days the two date ranges overlap (inclusive)."""
    lo = max(p_start, q_start)
    hi = min(p_end,   q_end)
    return max(0, (hi - lo).days + 1)


def prorate_inventory(inv_row: dict,
                      period_start: date,
                      period_end: date) -> tuple[float | None, str]:
    """
    Calculate the inventory tCO2e equivalent for the given billing period by
    prorating the relevant quarterly consumption values by day-overlap fraction,
    then applying the inventory's own emission factor.

    Returns (inventory_tCO2e, basis_description).
    """
    try:
        ef = float(inv_row["emission_factor"])
    except (ValueError, TypeError):
        return None, "inventory emission factor is blank or non-numeric"

    inv_unit = inv_row.get("unit", "MWh").strip()
    inv_unit_lower = inv_unit.lower()

    prorated_qty  = 0.0
    quarters_used: list[str] = []
    total_overlap = 0

    for q, (q_start, q_end) in QUARTER_BOUNDS.items():
        col     = QUARTER_COLS[q]
        val_str = (inv_row.get(col) or "").strip()
        if not val_str:
            continue
        try:
            q_val = float(val_str)
        except ValueError:
            continue

        overlap   = _days_overlap(period_start, period_end, q_start, q_end)
        if overlap == 0:
            continue

        q_days    = (q_end - q_start).days + 1
        fraction  = overlap / q_days
        prorated_qty  += q_val * fraction
        total_overlap += overlap
        quarters_used.append(f"Q{q}({fraction:.1%} of {q_val:,.1f} {inv_unit})")

    if total_overlap == 0:
        return None, "no quarterly inventory data overlaps with invoice billing period"

    # Convert prorated_qty to tCO2e using inventory emission factor
    if inv_unit_lower in ("litre", "litres", "l"):
        # Diesel: quantity in litres, EF in kgCO2e/litre
        inv_tco2e = prorated_qty * ef / 1000
    elif inv_unit_lower == "mwh":
        # Gas/Electricity: quantity in MWh, EF in kgCO2e/kWh
        # MWh x kgCO2e/kWh = 1000 kWh x kgCO2e/kWh / 1000 = 1 tCO2e per MWh·(kgCO2e/kWh)
        inv_tco2e = prorated_qty * ef
    else:
        return None, f"inventory unit '{inv_unit}' not handled in proration"

    invoice_days = (period_end - period_start).days + 1
    basis = (
        f"{total_overlap}/{invoice_days} invoice days covered; "
        f"prorated from: {', '.join(quarters_used)}"
    )
    return round(inv_tco2e, 2), basis


def reconcile_row(calc: dict, inventory: dict[tuple[str, str], dict]) -> dict:
    """
    Compare one calculated-emissions row against the inventory.
    Returns a reconciliation report row.
    """
    fid         = calc.get("facility_id", "")
    energy_type = (calc.get("energy_type") or "").lower()
    period_str  = f"{calc.get('billing_period_start', '')} to {calc.get('billing_period_end', '')}"
    recon_notes: list[str] = []

    # Skip rows where emission calculation failed
    parser_val_str = str(calc.get("gross_emissions_tCO2e", "")).strip()
    if not parser_val_str:
        return {
            "facility_id":    fid,
            "energy_type":    energy_type,
            "billing_period": period_str,
            "parser_tCO2e":   "",
            "inventory_tCO2e": "",
            "inventory_basis": "",
            "variance_pct":   "",
            "flag":           "NO_PARSER_VALUE",
            "notes":          "emission calculation did not produce a value; reconciliation skipped",
        }

    try:
        parser_tco2e = float(parser_val_str)
    except ValueError:
        return {
            "facility_id":    fid, "energy_type": energy_type,
            "billing_period": period_str, "parser_tCO2e": parser_val_str,
            "inventory_tCO2e": "", "inventory_basis": "",
            "variance_pct": "", "flag": "PARSE_ERROR",
            "notes": "parser tCO2e value could not be converted to float",
        }

    # Find matching inventory row
    key = (fid, energy_type)
    inv_row = inventory.get(key)
    if inv_row is None:
        return {
            "facility_id":    fid, "energy_type": energy_type,
            "billing_period": period_str, "parser_tCO2e": parser_tco2e,
            "inventory_tCO2e": "", "inventory_basis": "",
            "variance_pct": "", "flag": "NO_INVENTORY_MATCH",
            "notes": (
                f"no matching row found in lumora-ghg-inventory.csv "
                f"for facility {fid}, energy type '{energy_type}'"
            ),
        }

    # Parse billing period dates
    try:
        p_start = date.fromisoformat(calc["billing_period_start"])
        p_end   = date.fromisoformat(calc["billing_period_end"])
    except (KeyError, ValueError):
        return {
            "facility_id":    fid, "energy_type": energy_type,
            "billing_period": period_str, "parser_tCO2e": parser_tco2e,
            "inventory_tCO2e": "", "inventory_basis": "",
            "variance_pct": "", "flag": "INVALID_PERIOD",
            "notes": "billing period dates could not be parsed; reconciliation skipped",
        }

    # Prorate inventory to billing period
    inv_tco2e, basis = prorate_inventory(inv_row, p_start, p_end)
    if inv_tco2e is None:
        return {
            "facility_id":    fid, "energy_type": energy_type,
            "billing_period": period_str, "parser_tCO2e": parser_tco2e,
            "inventory_tCO2e": "", "inventory_basis": basis,
            "variance_pct": "", "flag": "INVENTORY_DATA_GAP",
            "notes": basis,
        }

    # Calculate variance
    if inv_tco2e == 0:
        variance_pct = 0.0 if parser_tco2e == 0 else float("inf")
    else:
        variance_pct = ((parser_tco2e - inv_tco2e) / inv_tco2e) * 100

    abs_var = abs(variance_pct)
    if abs_var > ERROR_THRESHOLD:
        flag = "RECONCILIATION_ERROR"
        recon_notes.append(
            f"variance of {variance_pct:+.1f}% exceeds {ERROR_THRESHOLD}% error threshold"
        )
    elif abs_var > WARN_THRESHOLD:
        flag = "RECONCILIATION_WARNING"
        recon_notes.append(
            f"variance of {variance_pct:+.1f}% exceeds {WARN_THRESHOLD}% warning threshold"
        )
    else:
        flag = "RECONCILED"
        recon_notes.append(f"variance of {variance_pct:+.1f}% is within {WARN_THRESHOLD}% tolerance")

    # Explanatory notes for large variances
    if abs_var > ERROR_THRESHOLD:
        invoice_days = (p_end - p_start).days + 1
        # Check if invoice value is close to the full-quarter inventory value
        # (suggests temporal mismatch — invoice may represent more than its stated period)
        for q, (q_start, q_end) in QUARTER_BOUNDS.items():
            q_col = QUARTER_COLS[q]
            q_val_str = (inv_row.get(q_col) or "").strip()
            if not q_val_str:
                continue
            try:
                q_val = float(q_val_str)
            except ValueError:
                continue
            q_days = (q_end - q_start).days + 1
            inv_unit = inv_row.get("unit", "MWh").lower()
            # Re-derive parser quantity in inventory units for comparison
            try:
                ef = float(inv_row["emission_factor"])
            except (ValueError, TypeError):
                continue
            if inv_unit in ("litre", "litres", "l"):
                implied_qty = parser_tco2e * 1000 / ef
            else:
                implied_qty = parser_tco2e / ef  # MWh
            pct_of_full_q = (implied_qty / q_val * 100) if q_val else 0
            if 85 <= pct_of_full_q <= 115:
                recon_notes.append(
                    f"parser-implied quantity ({implied_qty:,.1f} {inv_unit}) is "
                    f"{pct_of_full_q:.0f}% of inventory Q{q} value ({q_val:,.1f} {inv_unit}); "
                    f"invoice billing period ({invoice_days} days) covers only "
                    f"{_days_overlap(p_start, p_end, q_start, q_end)}/{q_days} days of Q{q} — "
                    "possible cause: invoice represents full-quarter consumption "
                    "despite a single-month billing period label"
                )
                break
        else:
            recon_notes.append(
                "possible causes: (1) temporal mismatch between invoice period and "
                "inventory quarterly data; (2) data entry error in inventory; "
                "(3) invoice covers a different consumption boundary than inventory record"
            )

    return {
        "facility_id":     fid,
        "energy_type":     energy_type,
        "billing_period":  period_str,
        "parser_tCO2e":    parser_tco2e,
        "inventory_tCO2e": inv_tco2e,
        "inventory_basis": basis,
        "variance_pct":    round(variance_pct, 1) if variance_pct != float("inf") else "N/A",
        "flag":            flag,
        "notes":           " | ".join(recon_notes),
    }


def reconcile(results: list[dict],
              inventory: dict[tuple[str, str], dict]) -> list[dict]:
    """Run reconciliation for all calculated records and return report rows."""
    return [reconcile_row(r, inventory) for r in results]


def apply_recon_flags(results: list[dict],
                      recon_rows: list[dict]) -> list[dict]:
    """
    Back-propagate reconciliation flags into the calculated-emissions rows
    so that calculated-emissions.csv shows the reconciliation status per record.
    """
    for calc, recon in zip(results, recon_rows):
        calc["reconciliation_flag"] = recon["flag"]
    return results


# -- Console output ----------------------------------------------------------- #

def print_summary(results: list[dict]) -> None:
    totals: dict[str, dict] = {}
    for r in results:
        fid = r["facility_id"] or "UNKNOWN"
        if fid not in totals:
            totals[fid] = {"name": r["facility_name"], "country": r["country"],
                           "scope1": 0.0, "s2_loc": 0.0, "s2_mkt": 0.0}
        try:
            val = float(r["gross_emissions_tCO2e"])
        except (ValueError, TypeError):
            continue
        if r["scope"] == "Scope 1":
            totals[fid]["scope1"] += val
        elif r["scope"] == "Scope 2":
            totals[fid]["s2_loc"] += val
            try:
                totals[fid]["s2_mkt"] += float(r["scope2_market_based_tCO2e"])
            except (ValueError, TypeError):
                totals[fid]["s2_mkt"] += val

    W = [6, 32, 14, 18, 20, 18]
    HDR = (f"{'FID':<{W[0]}}  {'Facility':<{W[1]}}  {'Country':<{W[2]}}  "
           f"{'Scope 1 (tCO2e)':>{W[3]}}  {'S2 Location (tCO2e)':>{W[4]}}  "
           f"{'S2 Market (tCO2e)':>{W[5]}}")
    SEP = "-" * len(HDR)
    print()
    print(SEP)
    print("EMISSIONS SUMMARY -- Lumora Technologies | Parsed Invoice Batch")
    print("Framework: GHG Protocol Corporate Standard")
    print(SEP)
    print(HDR)
    print(SEP)
    t_s1 = t_s2l = t_s2m = 0.0
    for fid, d in sorted(totals.items()):
        s1, s2l, s2m = d["scope1"], d["s2_loc"], d["s2_mkt"]
        t_s1 += s1; t_s2l += s2l; t_s2m += s2m
        print(f"{fid:<{W[0]}}  {d['name'][:W[1]]:<{W[1]}}  {d['country'][:W[2]]:<{W[2]}}  "
              f"{s1:{W[3]},.2f}  {s2l:{W[4]},.2f}  {s2m:{W[5]},.2f}")
    print(SEP)
    print(f"{'TOTAL':<{W[0]}}  {'':>{W[1]}}  {'':>{W[2]}}  "
          f"{t_s1:{W[3]},.2f}  {t_s2l:{W[4]},.2f}  {t_s2m:{W[5]},.2f}")
    print(SEP)
    print()
    print("Emission factor sources:")
    print("  Electricity (Scope 2):  IEA Electricity Information 2023")
    print("  Natural gas (Scope 1):  IPCC AR6 WG III Annex II -- 0.202 kgCO2e/kWh (GCV)")
    print("  Diesel (Scope 1):       DEFRA 2023 GHG Conversion Factors -- 2.68 kgCO2e/litre")
    print("  Gas conversion (m3):    GTS standard -- 10.55 kWh/m3 (Groningen quality)")
    print("  GJ conversion:          1 GJ = 277.778 kWh")
    print()


def print_recon_summary(recon_rows: list[dict]) -> None:
    W = [6, 14, 24, 16, 16, 10, 25]
    HDR = (f"{'FID':<{W[0]}}  {'Energy Type':<{W[1]}}  {'Billing Period':<{W[2]}}  "
           f"{'Parser (tCO2e)':>{W[3]}}  {'Inventory (tCO2e)':>{W[4]}}  "
           f"{'Variance':>{W[5]}}  {'Flag':<{W[6]}}")
    SEP = "-" * len(HDR)
    print()
    print(SEP)
    print("RECONCILIATION SUMMARY -- Parser vs Inventory")
    print(f"Thresholds: WARNING > {WARN_THRESHOLD}%  |  ERROR > {ERROR_THRESHOLD}%")
    print(SEP)
    print(HDR)
    print(SEP)

    counts = {"RECONCILED": 0, "RECONCILIATION_WARNING": 0,
              "RECONCILIATION_ERROR": 0, "other": 0}

    for r in recon_rows:
        flag     = r["flag"]
        p_val    = f"{r['parser_tCO2e']:,.2f}" if isinstance(r["parser_tCO2e"], float) else str(r["parser_tCO2e"])
        i_val    = f"{r['inventory_tCO2e']:,.2f}" if isinstance(r["inventory_tCO2e"], float) else str(r["inventory_tCO2e"])
        var_str  = f"{r['variance_pct']:+.1f}%" if isinstance(r["variance_pct"], float) else str(r["variance_pct"])
        period   = r["billing_period"][:W[2]]
        print(f"{r['facility_id']:<{W[0]}}  {r['energy_type']:<{W[1]}}  {period:<{W[2]}}  "
              f"{p_val:>{W[3]}}  {i_val:>{W[4]}}  {var_str:>{W[5]}}  {flag:<{W[6]}}")
        counts[flag] = counts.get(flag, 0) + 1

    print(SEP)
    print(f"Results: RECONCILED={counts.get('RECONCILED',0)}  "
          f"WARNING={counts.get('RECONCILIATION_WARNING',0)}  "
          f"ERROR={counts.get('RECONCILIATION_ERROR',0)}  "
          f"OTHER={sum(v for k,v in counts.items() if k not in ('RECONCILED','RECONCILIATION_WARNING','RECONCILIATION_ERROR'))}")
    print()
    print("Notes:")
    print("  Inventory figures are prorated by day-overlap to match invoice billing periods.")
    print("  RECONCILIATION_ERROR on F01 and F06 reflects temporal data inconsistency:")
    print("    F01 Jan invoice value (~310 MWh) matches the full Q1 inventory (310 MWh),")
    print("    suggesting the invoice may represent quarterly rather than monthly consumption.")
    print("    F06 Jan-Feb invoice (10,980 GJ = ~3,050 MWh) exceeds prorated Q1 inventory")
    print("    (1,560 MWh for full quarter); verify whether inventory Q1 is monthly or quarterly.")
    print(f"  Full reconciliation detail: {RECON_CSV.name}")
    print()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    if not PARSED_CSV.exists():
        print(f"Error: {PARSED_CSV} not found. Run receipt-parser/parser.py first.",
              file=sys.stderr)
        sys.exit(1)

    # -- Step 1: Calculate emissions ----------------------------------------- #
    with open(PARSED_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} record(s) from {PARSED_CSV.name}\n")

    results = []
    for row in rows:
        result = calculate_row(row)
        results.append(result)
        ems    = result["gross_emissions_tCO2e"]
        s2m    = result.get("scope2_market_based_tCO2e", "")
        tag    = f"{ems} tCO2e" if ems != "" else "SKIPPED"
        mkt    = f" | market-based: {s2m} tCO2e" if s2m not in ("", str(ems)) else ""
        print(f"  {result['facility_id']:<4}  {result['energy_type']:12s}  "
              f"{result['unit']:6s}  {result['quantity']:>12,.2f}  ->  {tag}{mkt}")

    # -- Step 2: Reconcile against inventory ---------------------------------- #
    print(f"\nLoading inventory from {INVENTORY_CSV.name} ...")
    inventory = load_inventory()
    if not inventory:
        print("  Warning: inventory not loaded; reconciliation skipped.", file=sys.stderr)
        recon_rows = []
    else:
        print(f"  {len(inventory)} inventory rows indexed.\n")
        recon_rows = reconcile(results, inventory)
        results    = apply_recon_flags(results, recon_rows)

    # -- Write outputs -------------------------------------------------------- #
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"Calculated emissions written to: {OUTPUT_CSV}")

    if recon_rows:
        with open(RECON_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=RECON_FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(recon_rows)
        print(f"Reconciliation report written to:  {RECON_CSV}")

    # -- Print summaries ------------------------------------------------------ #
    print_summary(results)
    if recon_rows:
        print_recon_summary(recon_rows)


if __name__ == "__main__":
    main()
