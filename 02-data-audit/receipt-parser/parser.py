#!/usr/bin/env python3
"""
receipt-parser/parser.py
Lumora Technologies — GHG Inventory Data Pipeline

Extracts structured energy consumption data from utility invoices using Claude.
Outputs parsed-invoices.csv with confidence scores and anomaly flags.

Authentication (in priority order):
  1. ANTHROPIC_API_KEY env var  → uses the Anthropic Python SDK directly
  2. No API key                 → falls back to the `claude` CLI via subprocess
                                  (works automatically inside Claude Code sessions)

Usage:
    python parser.py                          # auto-detects auth method
    ANTHROPIC_API_KEY=sk-ant-... python parser.py  # force SDK mode

Requirements (SDK mode only):
    pip install anthropic
"""

import os
import re
import json
import csv
import sys
import platform
import shutil
import subprocess
from pathlib import Path
from datetime import date

# ── Configuration ──────────────────────────────────────────────────────────── #

MODEL = "claude-sonnet-4-6"
INVOICE_DIR = Path(__file__).parent / "invoices"
OUTPUT_CSV = Path(__file__).parent / "parsed-invoices.csv"
MAX_TOKENS = 1024

# Fields the model must attempt to extract
REQUIRED_FIELDS = [
    "facility_id", "facility_name", "country", "energy_type",
    "quantity", "unit", "billing_period_start", "billing_period_end",
    "cost", "currency", "supplier",
]

# Column order in the output CSV
OUTPUT_FIELDS = REQUIRED_FIELDS + [
    "confidence_score", "anomaly_flags", "extraction_notes", "source_file"
]

# Missing any of these critical fields triggers a Low confidence score
CRITICAL_FIELDS = {
    "facility_id", "energy_type", "quantity", "unit",
    "billing_period_start", "billing_period_end",
}

# Expected consumption ranges per (facility_type, energy_type) per billing period.
# Electricity and natural gas values are normalised to kWh for comparison.
# Diesel values remain in litres (not converted to kWh).
EXPECTED_RANGES = {
    ("office",        "electricity"): (50_000,      800_000),
    ("office",        "natural_gas"): (20_000,      400_000),
    ("manufacturing", "electricity"): (500_000,  20_000_000),
    ("manufacturing", "natural_gas"): (100_000,   5_000_000),
    ("manufacturing", "diesel"):      (500,          30_000),
    ("warehouse",     "electricity"): (50_000,    1_500_000),
    ("warehouse",     "natural_gas"): (10_000,      300_000),
}

# Lumora facility type lookup
FACILITY_TYPES = {
    "F01": "office", "F02": "manufacturing", "F03": "office",
    "F04": "manufacturing", "F05": "manufacturing", "F06": "manufacturing",
    "F07": "office", "F08": "warehouse", "F09": "office",
}

# Conversion factors to kWh (for range-checking only; output preserves original units)
UNIT_TO_KWH = {
    "kwh": 1.0, "mwh": 1_000.0, "gwh": 1_000_000.0,
    "gj": 277.78, "mj": 0.27778,
    "m3": 10.55,    # natural gas, Groningen quality (GTS standard)
    "therm": 29.3,
}

# ── Prompts ────────────────────────────────────────────────────────────────── #

_FEW_SHOT = """\
EXAMPLE INPUT:
--------------
ENERGIEBEDRIJF AMSTERDAM
Invoice No: AMS-2023-00441  |  Date: 10 March 2023
Customer: Lumora Technologies B.V.
Facility: Amsterdam HQ (F01)  |  Country: Netherlands
Service Period: 01 February 2023 to 28 February 2023
Service Type: Electricity
Consumption: 295,180 kWh  |  Rate: EUR 0.1842/kWh
Subtotal (excl. VAT): EUR 55,562.16  |  VAT 21%: EUR 11,668.05
TOTAL DUE: EUR 67,230.21
Supplier: Energiebedrijf Amsterdam

EXAMPLE OUTPUT:
---------------
{
  "facility_id": "F01",
  "facility_name": "Amsterdam HQ",
  "country": "Netherlands",
  "energy_type": "electricity",
  "quantity": 295180,
  "unit": "kWh",
  "billing_period_start": "2023-02-01",
  "billing_period_end": "2023-02-28",
  "cost": 67230.21,
  "currency": "EUR",
  "supplier": "Energiebedrijf Amsterdam",
  "extraction_notes": "All fields present and unambiguous. VAT-inclusive total used for cost."
}
"""

SYSTEM_PROMPT = f"""\
You are an expert data extraction agent specialising in energy utility invoices \
for corporate GHG accounting under the GHG Protocol Corporate Standard.

Your task: extract structured fields from the utility bill text provided by the \
user. Return ONLY a valid JSON object — no explanation, no markdown, no code \
fences, no surrounding text of any kind.

REQUIRED OUTPUT FIELDS:
  facility_id            Lumora facility code (F01-F09), or null if not determinable
  facility_name          Facility name as stated on the invoice
  country                Country where the facility is located
  energy_type            One of: electricity | natural_gas | diesel | other
  quantity               Numeric consumption value only (plain number, no commas, no units)
  unit                   Unit exactly as stated on the invoice (e.g. kWh, MWh, m3, GJ, litres)
  billing_period_start   ISO 8601 date YYYY-MM-DD
  billing_period_end     ISO 8601 date YYYY-MM-DD
  cost                   Total invoice amount as a plain number (VAT-inclusive if stated)
  currency               ISO 4217 code (e.g. EUR, USD, VND, MYR, MXN)
  supplier               Name of the energy supplier as stated
  extraction_notes       One sentence noting any ambiguities, assumptions, or data quality concerns

EXTRACTION RULES:
1. Return quantity as a plain number — strip commas, periods used as thousands
   separators, spaces, and unit suffixes.
2. If billing period is given as a quarter (e.g. Q1 2023), map to the first and
   last calendar day of that quarter (Q1: Jan 1 – Mar 31).
3. Use the VAT-inclusive total for cost where available; otherwise use the
   pre-tax subtotal. Return cost as a plain number with no currency symbols.
4. Infer facility_id from the facility name or code if not explicitly labelled.
5. For natural gas invoiced in m3, preserve m3 as the unit — do not convert.
6. Where an invoice lists both active energy (kWh) and reactive energy (kVArh),
   extract the active energy only. Reactive energy is not used for GHG reporting.
7. If a field cannot be reliably determined, return null — never fabricate a value.

{_FEW_SHOT}
Now extract all fields from the invoice provided by the user and return the \
JSON object only."""


# ── Auth detection ─────────────────────────────────────────────────────────── #

def _using_sdk() -> bool:
    """Return True if ANTHROPIC_API_KEY is set; False to fall back to CLI."""
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


# ── Extraction ─────────────────────────────────────────────────────────────── #

def load_invoice(filepath: Path) -> str:
    """Read invoice text file as UTF-8."""
    return filepath.read_text(encoding="utf-8")


def _parse_response(raw: str) -> dict:
    """Strip optional markdown fences and parse JSON from a model response."""
    raw = raw.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


def _extract_via_sdk(invoice_text: str) -> dict:
    """
    Extract fields using the Anthropic Python SDK.
    The system prompt is marked cache_control: ephemeral so it is served from
    cache for invoices 2 onwards, reducing latency and token cost.
    """
    import anthropic  # imported here so CLI-only runs don't require the package

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": invoice_text}],
    )
    return _parse_response(response.content[0].text)


def _find_claude() -> list[str]:
    """
    Return the command prefix needed to invoke the claude CLI on this platform.

    On Windows, claude is installed by npm as claude.cmd — a batch wrapper that
    must be executed via cmd /c rather than called directly as a binary.
    Resolution order:
      1. shutil.which() for 'claude' / 'claude.cmd' / 'claude.exe' (covers any
         platform where the npm bin dir is already on PATH)
      2. Common Windows npm install locations (APPDATA\\npm, home\\AppData\\...)
      3. cmd /c claude as a last-resort Windows fallback
      4. Plain ['claude'] on non-Windows
    """
    if platform.system() == "Windows":
        # shutil.which resolves PATH including the npm scripts folder
        for name in ("claude", "claude.cmd", "claude.exe"):
            found = shutil.which(name)
            if found:
                # .cmd files must be invoked through cmd /c on Windows
                if found.lower().endswith(".cmd"):
                    return ["cmd", "/c", found]
                return [found]

        # Fallback: check the two most common npm global install paths directly
        appdata = os.environ.get("APPDATA", "")
        candidates = [
            Path(appdata) / "npm" / "claude.cmd",
            Path.home() / "AppData" / "Roaming" / "npm" / "claude.cmd",
        ]
        for p in candidates:
            if p.exists():
                print(f"  [found claude at {p}]")
                return ["cmd", "/c", str(p)]

        # Last resort: let cmd.exe search PATH itself
        return ["cmd", "/c", "claude"]

    # macOS / Linux: standard lookup
    found = shutil.which("claude")
    return [found] if found else ["claude"]


def _extract_via_cli(invoice_text: str) -> dict:
    """
    Fallback extraction using the `claude` CLI (Claude Code).
    Works inside Claude Code sessions without a separate API key.

    The prompt is passed via stdin rather than as a -p argument.
    This avoids the Windows cmd.exe command-line length limit (~8191 chars),
    which silently truncates long -p arguments and produces empty output.

    Claude detects non-TTY stdin and runs non-interactively.
    Two strategies are tried in order:
      1. claude -p  (explicit print/non-interactive mode, prompt via stdin)
      2. claude     (implicit non-interactive mode when stdin is a pipe)
    """
    prompt = f"{SYSTEM_PROMPT}\n\nINVOICE TO PROCESS:\n{invoice_text}"
    base_cmd = _find_claude()

    for cmd in [base_cmd + ["-p"], base_cmd]:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
        # Response may appear on stdout or stderr depending on claude version
        output = result.stdout.strip() or result.stderr.strip()
        if output:
            return _parse_response(output)

    raise RuntimeError(
        "claude CLI returned no output from either strategy. "
        f"base_cmd={base_cmd}, last exit code={result.returncode}. "
        "Ensure claude is authenticated (run `claude` once interactively)."
    )


def extract_fields(invoice_text: str) -> dict:
    """
    Dispatch to SDK or CLI based on whether ANTHROPIC_API_KEY is set.
    Returns the extracted fields as a Python dict.
    """
    if _using_sdk():
        return _extract_via_sdk(invoice_text)
    return _extract_via_cli(invoice_text)


# ── Confidence scoring ─────────────────────────────────────────────────────── #

def calculate_confidence(record: dict, anomalies: list[str]) -> str:
    """
    Score record confidence as High / Medium / Low.

    High   — all required fields present; no anomaly flags
    Medium — 1-2 required fields missing, OR only non-critical anomalies
    Low    — 3+ required fields missing, OR any critical anomaly flag
             (MISSING_CRITICAL_FIELD, QUANTITY_OUT_OF_RANGE, UNIT_MISMATCH)
    """
    missing = [f for f in REQUIRED_FIELDS if record.get(f) is None]

    critical_prefixes = (
        "MISSING_CRITICAL_FIELD",
        "QUANTITY_OUT_OF_RANGE",
        "UNIT_MISMATCH",
    )
    has_critical_anomaly = any(
        a.startswith(p) for a in anomalies for p in critical_prefixes
    )

    if len(missing) >= 3 or has_critical_anomaly:
        return "Low"
    if missing or anomalies:
        return "Medium"
    return "High"


# ── Anomaly detection ──────────────────────────────────────────────────────── #

def _normalise_to_kwh(quantity: float, unit: str) -> float | None:
    """
    Convert a consumption value to kWh using the unit lookup table.
    Returns None if the unit is not recognised.
    Diesel is not converted (ranges are already in litres).
    """
    factor = UNIT_TO_KWH.get(unit.lower().strip())
    return quantity * factor if factor is not None else None


def detect_anomalies(record: dict, processed: list[dict]) -> list[str]:
    """
    Check for five anomaly types and return a list of flag strings.

    1. MISSING_CRITICAL_FIELD / MISSING_FIELD  — required field is null
    2. QUANTITY_OUT_OF_RANGE                   — extreme outlier vs expected range
    3. UNIT_MISMATCH                           — value fits a different common unit
    4. BILLING_PERIOD_OVERLAP                  — period overlaps a prior invoice
    5. BILLING_PERIOD_GAP                      — >5-day gap between invoices

    `processed` contains all records already parsed in this run (used for
    overlap/gap detection).
    """
    flags = []

    # 1. Missing fields ───────────────────────────────────────────────────── #
    for field in REQUIRED_FIELDS:
        if record.get(field) is None:
            tag = (
                "MISSING_CRITICAL_FIELD" if field in CRITICAL_FIELDS
                else "MISSING_FIELD"
            )
            flags.append(f"{tag}:{field}")

    quantity = record.get("quantity")
    unit = (record.get("unit") or "").strip()
    energy_type = (record.get("energy_type") or "").lower()
    facility_id = record.get("facility_id")

    if quantity is not None and unit and facility_id:
        facility_type = FACILITY_TYPES.get(facility_id)
        range_key = (facility_type, energy_type) if facility_type else None
        expected = EXPECTED_RANGES.get(range_key) if range_key else None

        # Normalise to kWh for range check; diesel stays in litres
        if energy_type == "diesel":
            norm_qty: float | None = float(quantity)
        else:
            norm_qty = _normalise_to_kwh(float(quantity), unit)

        if expected is not None and norm_qty is not None:
            lo, hi = expected

            # 2. Extreme out-of-range (>10× bounds — likely a data or unit error)
            if norm_qty < lo * 0.1 or norm_qty > hi * 10:
                flags.append(
                    f"QUANTITY_OUT_OF_RANGE:{quantity} {unit} "
                    f"(normalised {norm_qty:,.0f}; expected {lo:,}–{hi:,})"
                )
            # 3. Within 10× but still outside — check if a unit swap fixes it
            elif not (lo <= norm_qty <= hi):
                alt_map = {
                    "kwh":  ("mwh",  1_000.0),
                    "mwh":  ("kwh",  1 / 1_000.0),
                    "gj":   ("mwh",  277.78),
                    "m3":   ("kwh",  10.55),
                }
                alt = alt_map.get(unit.lower())
                if alt:
                    alt_name, alt_factor = alt
                    alt_norm = float(quantity) * alt_factor
                    if lo <= alt_norm <= hi:
                        flags.append(
                            f"UNIT_MISMATCH:{quantity} {unit} is outside expected "
                            f"range but would fit as {alt_name} "
                            f"(norm={norm_qty:,.0f}, alt={alt_norm:,.0f})"
                        )
                    else:
                        flags.append(
                            f"QUANTITY_OUT_OF_RANGE:{quantity} {unit} "
                            f"(normalised {norm_qty:,.0f}; expected {lo:,}–{hi:,})"
                        )
                else:
                    flags.append(
                        f"QUANTITY_OUT_OF_RANGE:{quantity} {unit} "
                        f"(normalised {norm_qty:,.0f}; expected {lo:,}–{hi:,})"
                    )

    # 4 & 5. Billing period overlap and gap ──────────────────────────────── #
    fid = record.get("facility_id")
    start_str = record.get("billing_period_start")
    end_str = record.get("billing_period_end")

    if fid and start_str and end_str:
        try:
            r_start = date.fromisoformat(start_str)
            r_end = date.fromisoformat(end_str)
        except ValueError:
            r_start = r_end = None

        if r_start and r_end:
            for prev in processed:
                if prev.get("facility_id") != fid:
                    continue
                try:
                    p_start = date.fromisoformat(prev["billing_period_start"])
                    p_end = date.fromisoformat(prev["billing_period_end"])
                except (KeyError, TypeError, ValueError):
                    continue

                # Overlap: periods intersect
                if r_start <= p_end and r_end >= p_start:
                    flags.append(
                        f"BILLING_PERIOD_OVERLAP:overlaps with period "
                        f"{prev['billing_period_start']}–{prev['billing_period_end']}"
                    )
                # Gap: more than 5 days between consecutive periods
                elif (r_start - p_end).days > 5:
                    flags.append(
                        f"BILLING_PERIOD_GAP:{(r_start - p_end).days} days "
                        f"between {prev['billing_period_end']} and {start_str}"
                    )

    return flags


# ── Main pipeline ──────────────────────────────────────────────────────────── #

def parse_all_invoices() -> list[dict]:
    """
    Process every .txt file in the invoices/ directory.
    Returns a list of enriched record dicts ready for CSV output.
    """
    mode = "SDK (ANTHROPIC_API_KEY)" if _using_sdk() else "CLI (claude)"
    print(f"Auth mode: {mode}\n")

    invoice_files = sorted(INVOICE_DIR.glob("*.txt"))

    if not invoice_files:
        print(f"No .txt invoice files found in {INVOICE_DIR}", file=sys.stderr)
        return []

    records: list[dict] = []

    for filepath in invoice_files:
        print(f"Processing: {filepath.name}")
        try:
            invoice_text = load_invoice(filepath)
            extracted = extract_fields(invoice_text)

            # Coerce quantity to float (model may return string or int)
            if extracted.get("quantity") is not None:
                try:
                    extracted["quantity"] = float(
                        str(extracted["quantity"]).replace(",", "")
                    )
                except (ValueError, TypeError):
                    extracted["quantity"] = None

            anomalies = detect_anomalies(extracted, records)
            confidence = calculate_confidence(extracted, anomalies)

            extracted["confidence_score"] = confidence
            extracted["anomaly_flags"] = "; ".join(anomalies) if anomalies else ""
            extracted["source_file"] = filepath.name

            records.append(extracted)

            status = f"  -> {confidence} confidence"
            if anomalies:
                preview = anomalies[0][:70]
                status += f" | {len(anomalies)} flag(s): {preview}"
            print(status)

        except json.JSONDecodeError as exc:
            print(f"  -> JSON parse error: {exc}", file=sys.stderr)
            records.append({
                "source_file": filepath.name,
                "confidence_score": "Low",
                "anomaly_flags": f"PARSE_ERROR:{exc}",
                "extraction_notes": "API response could not be parsed as JSON.",
            })
        except Exception as exc:  # noqa: BLE001
            print(f"  -> Error processing {filepath.name}: {exc}", file=sys.stderr)

    return records


def write_csv(records: list[dict], output_path: Path) -> None:
    """Write extracted records to CSV with a fixed column order."""
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=OUTPUT_FIELDS, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(records)

    high = sum(1 for r in records if r.get("confidence_score") == "High")
    med  = sum(1 for r in records if r.get("confidence_score") == "Medium")
    low  = sum(1 for r in records if r.get("confidence_score") == "Low")

    print(f"\nOutput written to: {output_path}")
    print(f"Records processed: {len(records)}")
    print(f"Confidence: High={high}  Medium={med}  Low={low}")


if __name__ == "__main__":
    results = parse_all_invoices()
    if results:
        write_csv(results, OUTPUT_CSV)
