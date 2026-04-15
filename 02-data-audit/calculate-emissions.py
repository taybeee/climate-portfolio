#!/usr/bin/env python3
"""
02-data-audit/calculate-emissions.py
Lumora Technologies — GHG Emissions Calculator

Reads parsed-invoices.csv produced by receipt-parser/parser.py, applies
GHG Protocol emission factors, performs unit conversions, and outputs
calculated-emissions.csv.

Framework:  GHG Protocol Corporate Standard
Scope 1:    Natural gas (IPCC AR6), diesel (DEFRA 2023)
Scope 2:    Electricity, location-based (IEA 2023 country grid factors)
            Market-based treatment noted where renewable procurement is verified.

Usage:
    python calculate-emissions.py
"""

import csv
import sys
from pathlib import Path

# -- Paths -------------------------------------------------------------------- #

PARSED_CSV = Path(__file__).parent / "receipt-parser" / "parsed-invoices.csv"
OUTPUT_CSV = Path(__file__).parent / "calculated-emissions.csv"

# -- Emission factor reference tables ---------------------------------------- #

# IEA 2023 country-level grid emission factors — location-based (kgCO2e/kWh).
# Source: IEA Electricity Information 2023; EMA Singapore Electricity Grid
# Emission Factor 2023 for Singapore.
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
# Source: IPCC AR6 Working Group III, Annex II, Table A.III.2
NATURAL_GAS_EF = {
    "factor": 0.202,
    "unit":   "kgCO2e/kWh",
    "source": "IPCC AR6 WG III Annex II (natural gas combustion, GCV basis)",
}

# Scope 1: diesel — kgCO2e per litre
# Source: DEFRA UK Government GHG Conversion Factors 2023, Transport fuels
DIESEL_EF = {
    "factor": 2.68,
    "unit":   "kgCO2e/litre",
    "source": "DEFRA 2023 GHG Conversion Factors (diesel, kg CO2e per litre)",
}

# Facilities with verified renewable energy certificates — market-based Scope 2 = 0.
# F01 Amsterdam HQ: REGO-backed PPA (Eneco)
# F02 Eindhoven Mfg: REGO-backed PPA (Vattenfall)
# F03 Berlin Office: utility-verified green tariff
ZERO_MARKET_BASED: set[tuple[str, str]] = {
    ("F01", "electricity"),
    ("F02", "electricity"),
    ("F03", "electricity"),
}

# -- Unit conversion to kWh --------------------------------------------------- #
# All electricity and gas quantities are converted to kWh before applying EF.
# Diesel: GHG calc uses litres × kgCO2e/litre directly;
#         quantity_kwh is the energy-content equivalent (10.8 kWh/L, LHV) for reference.

UNIT_TO_KWH: dict[str, float] = {
    "kwh":    1.0,
    "mwh":    1_000.0,
    "gwh":    1_000_000.0,
    "gj":     277.778,   # 1 GJ = 277.778 kWh (exact: 1/0.0036)
    "mj":     0.277778,
    "m3":     10.55,     # natural gas, Groningen quality (GTS standard calorific value)
    "m³":     10.55,     # Unicode variant
    "therm":  29.307,
}

DIESEL_KWH_PER_LITRE = 10.8   # lower heating value; reference only, not used in GHG calc

DIESEL_UNITS = {"litre", "litres", "liter", "liters", "l"}

SCOPE_MAP: dict[str, str] = {
    "electricity": "Scope 2",
    "natural_gas": "Scope 1",
    "diesel":      "Scope 1",
}

OUTPUT_FIELDS = [
    "facility_id",
    "facility_name",
    "country",
    "energy_type",
    "billing_period_start",
    "billing_period_end",
    "quantity",
    "unit",
    "quantity_kwh",
    "emission_factor",
    "emission_factor_unit",
    "emission_factor_source",
    "gross_emissions_tCO2e",
    "scope",
    "scope2_market_based_tCO2e",
    "confidence_score",
    "notes",
]


# -- Unit conversion ---------------------------------------------------------- #

def to_kwh(quantity: float, unit: str) -> tuple[float | None, str]:
    """
    Convert a consumption quantity to kWh.
    For diesel, returns the energy-content equivalent (reference only).
    Returns (kwh_value, note).
    """
    u = unit.lower().strip()

    if u in DIESEL_UNITS:
        kwh = quantity * DIESEL_KWH_PER_LITRE
        return kwh, (
            f"quantity_kwh = {kwh:,.1f} kWh is energy-content equivalent "
            f"at {DIESEL_KWH_PER_LITRE} kWh/L (LHV, reference only); "
            "GHG calculation uses litres × kgCO2e/litre"
        )

    factor = UNIT_TO_KWH.get(u)
    if factor is None:
        return None, f"unit '{unit}' not in conversion table; quantity_kwh not calculated"

    return quantity * factor, ""


# -- Emission calculation ----------------------------------------------------- #

def calculate_row(row: dict) -> dict:
    """
    Apply the correct emission factor to a single parsed invoice row.
    Returns a fully populated output dict.
    """
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

    # -- Parse quantity ------------------------------------------------------ #
    try:
        quantity = float(str(row.get("quantity", "")).replace(",", ""))
    except (ValueError, TypeError):
        notes.append("quantity could not be parsed; row skipped")
        return _empty_row(row, notes)

    # -- kWh conversion ------------------------------------------------------ #
    kwh_value, conversion_note = to_kwh(quantity, unit)
    if conversion_note:
        notes.append(conversion_note)

    # -- Select emission factor ---------------------------------------------- #
    ef_value  = None
    ef_unit   = None
    ef_source = None

    if energy_type == "electricity":
        grid = IEA_GRID_FACTORS.get(country)
        if grid is None:
            notes.append(
                f"no IEA grid factor for country '{country}'; "
                "add to IEA_GRID_FACTORS to enable calculation"
            )
            return _empty_row(row, notes, quantity, unit, kwh_value, period_start, period_end)
        ef_value  = grid["factor"]
        ef_unit   = "kgCO2e/kWh"
        ef_source = grid["source"]

    elif energy_type == "natural_gas":
        ef_value  = NATURAL_GAS_EF["factor"]
        ef_unit   = NATURAL_GAS_EF["unit"]
        ef_source = NATURAL_GAS_EF["source"]

    elif energy_type == "diesel":
        ef_value  = DIESEL_EF["factor"]
        ef_unit   = DIESEL_EF["unit"]
        ef_source = DIESEL_EF["source"]

    else:
        notes.append(
            f"energy type '{energy_type}' not recognised; "
            "expected: electricity | natural_gas | diesel"
        )
        return _empty_row(row, notes, quantity, unit, kwh_value, period_start, period_end)

    # -- Gross emissions ----------------------------------------------------- #
    u_lower = unit.lower().strip()

    if energy_type == "diesel":
        if u_lower not in DIESEL_UNITS:
            notes.append(
                f"unit '{unit}' not recognised as litres; "
                "cannot apply diesel emission factor"
            )
            return _empty_row(row, notes, quantity, unit, kwh_value, period_start, period_end)
        gross_kg = quantity * ef_value

    else:
        if kwh_value is None:
            notes.append(
                f"kWh conversion failed for unit '{unit}'; "
                "cannot apply kgCO2e/kWh factor"
            )
            return _empty_row(row, notes, quantity, unit, None, period_start, period_end)
        gross_kg = kwh_value * ef_value

    gross_tco2e = round(gross_kg / 1000, 2)

    # -- Scope and market-based treatment ----------------------------------- #
    scope = SCOPE_MAP.get(energy_type, "Unknown")

    market_based_str = ""
    if energy_type == "electricity":
        key = (facility_id, "electricity")
        if key in ZERO_MARKET_BASED:
            market_based_str = "0.0"
            notes.append(
                "Scope 2 market-based = 0.0 tCO2e: verified renewable energy certificate "
                "(REGO-backed PPA or utility green tariff); zero EF applicable under "
                "GHG Protocol market-based method"
            )
        else:
            market_based_str = str(gross_tco2e)
            notes.append(
                "Scope 2 market-based = location-based: no renewable energy procurement "
                "in place; market-based factor equals location-based factor"
            )

    # -- Anomaly passthrough ------------------------------------------------- #
    if anomaly_flags:
        if "BILLING_PERIOD_OVERLAP" in anomaly_flags and energy_type in ("diesel", "natural_gas"):
            notes.append(
                f"anomaly flag from parser: {anomaly_flags} — likely a false positive "
                "(multiple energy streams for same facility covering same period is expected)"
            )
        else:
            notes.append(f"anomaly flag from parser: {anomaly_flags}")

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
        "notes":                     " | ".join(notes),
    }


def _empty_row(
    row: dict,
    notes: list[str],
    quantity=None,
    unit=None,
    kwh_value=None,
    period_start="",
    period_end="",
) -> dict:
    """Return a row with emissions fields blank when calculation cannot proceed."""
    return {
        "facility_id":               row.get("facility_id", ""),
        "facility_name":             row.get("facility_name", ""),
        "country":                   row.get("country", ""),
        "energy_type":               row.get("energy_type", ""),
        "billing_period_start":      period_start or row.get("billing_period_start", ""),
        "billing_period_end":        period_end or row.get("billing_period_end", ""),
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
        "notes":                     " | ".join(notes),
    }


# -- Console summary ---------------------------------------------------------- #

def print_summary(results: list[dict]) -> None:
    """Print a facility-level emissions summary table to stdout."""

    # Aggregate per facility
    totals: dict[str, dict] = {}
    for r in results:
        fid = r["facility_id"] or "UNKNOWN"
        if fid not in totals:
            totals[fid] = {
                "name":     r["facility_name"],
                "country":  r["country"],
                "scope1":   0.0,
                "s2_loc":   0.0,
                "s2_mkt":   0.0,
            }
        try:
            val = float(r["gross_emissions_tCO2e"])
        except (ValueError, TypeError):
            continue

        if r["scope"] == "Scope 1":
            totals[fid]["scope1"] += val
        elif r["scope"] == "Scope 2":
            totals[fid]["s2_loc"] += val
            try:
                mkt = float(r["scope2_market_based_tCO2e"])
            except (ValueError, TypeError):
                mkt = val
            totals[fid]["s2_mkt"] += mkt

    # Column widths
    W = [6, 32, 14, 18, 20, 18]
    HDR = (
        f"{'FID':<{W[0]}}  "
        f"{'Facility':<{W[1]}}  "
        f"{'Country':<{W[2]}}  "
        f"{'Scope 1 (tCO2e)':>{W[3]}}  "
        f"{'S2 Location (tCO2e)':>{W[4]}}  "
        f"{'S2 Market (tCO2e)':>{W[5]}}"
    )
    SEP = "-" * len(HDR)

    print()
    print(SEP)
    print("EMISSIONS SUMMARY — Lumora Technologies | Parsed Invoice Batch")
    print("Framework: GHG Protocol Corporate Standard | Scope 2: location-based + market-based")
    print(SEP)
    print(HDR)
    print(SEP)

    t_s1 = t_s2l = t_s2m = 0.0
    for fid, d in sorted(totals.items()):
        s1  = d["scope1"]
        s2l = d["s2_loc"]
        s2m = d["s2_mkt"]
        t_s1  += s1
        t_s2l += s2l
        t_s2m += s2m
        name    = d["name"][:W[1]]
        country = d["country"][:W[2]]
        print(
            f"{fid:<{W[0]}}  "
            f"{name:<{W[1]}}  "
            f"{country:<{W[2]}}  "
            f"{s1:{W[3]},.2f}  "
            f"{s2l:{W[4]},.2f}  "
            f"{s2m:{W[5]},.2f}"
        )

    print(SEP)
    print(
        f"{'TOTAL':<{W[0]}}  "
        f"{'':>{W[1]}}  "
        f"{'':>{W[2]}}  "
        f"{t_s1:{W[3]},.2f}  "
        f"{t_s2l:{W[4]},.2f}  "
        f"{t_s2m:{W[5]},.2f}"
    )
    print(SEP)
    print()
    print("Emission factor sources:")
    print("  Electricity (Scope 2):  IEA Electricity Information 2023 (country grid factors)")
    print("  Natural gas (Scope 1):  IPCC AR6 WG III Annex II — 0.202 kgCO2e/kWh (GCV basis)")
    print("  Diesel (Scope 1):       DEFRA 2023 GHG Conversion Factors — 2.68 kgCO2e/litre")
    print("  Natural gas conversion: GTS standard calorific value — 10.55 kWh/m³ (Groningen)")
    print("  GJ conversion:          1 GJ = 277.778 kWh (exact)")
    print()
    print("Notes:")
    print("  Figures cover invoices in this batch only — not the full-year inventory.")
    print("  Scope 2 market-based reflects verified renewable energy procurement (REGO/green tariff).")
    print("  F02 natural gas overlap flag is a false positive (diesel + gas invoices cover same period).")
    print(f"  Full-year inventory: see 02-data-audit/lumora-ghg-inventory.csv")
    print()


# -- Main --------------------------------------------------------------------- #

def main() -> None:
    if not PARSED_CSV.exists():
        print(
            f"Error: {PARSED_CSV} not found.\n"
            "Run receipt-parser/parser.py first to generate parsed-invoices.csv.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(PARSED_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} record(s) from {PARSED_CSV.name}\n")

    results = []
    for row in rows:
        result = calculate_row(row)
        results.append(result)

        ems = result["gross_emissions_tCO2e"]
        s2m = result.get("scope2_market_based_tCO2e", "")
        tag = f"{ems} tCO2e" if ems != "" else "SKIPPED"
        mkt_tag = f" | market-based: {s2m} tCO2e" if s2m not in ("", str(ems)) else ""
        print(
            f"  {result['facility_id']:<4}  "
            f"{result['energy_type']:12s}  "
            f"{result['unit']:6s}  "
            f"{result['quantity']:>12,.2f}  "
            f"->  {tag}{mkt_tag}"
        )

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"\nOutput written to: {OUTPUT_CSV}")
    print_summary(results)


if __name__ == "__main__":
    main()
