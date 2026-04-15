# Receipt Parser — Lumora Technologies GHG Inventory

## What This Is

A Python extraction pipeline that reads utility invoice text files, sends each one to the Anthropic API (Claude), and returns structured energy consumption data as a clean CSV. It automates the most operationally tedious part of Scope 1 and 2 inventory work: extracting activity data from unstructured or inconsistently formatted supplier documents.

This is the RAG document ingestion pattern described in `CLAUDE.md`: extract structured fields first, validate against an expected schema, flag anomalies before emissions are calculated, and return a confidence score per record.

## How to Run

### Prerequisites

- Python 3.11+
- Anthropic API key set as the `ANTHROPIC_API_KEY` environment variable
- Install dependencies:

```bash
pip install anthropic
```

### Running the Parser

From the `receipt-parser/` directory:

```bash
python parser.py
```

The script will:
1. Read all `.txt` files from `invoices/`
2. Send each invoice to Claude with a structured extraction prompt
3. Score each record for confidence (High / Medium / Low)
4. Detect and flag anomalies
5. Write all results to `parsed-invoices.csv`

### Expected Output

```
Processing: invoice-F01-electricity-jan2023.txt
  -> High confidence
Processing: invoice-F02-diesel-q1-2023.txt
  -> High confidence
Processing: invoice-F02-gas-q1-2023.txt
  -> High confidence
Processing: invoice-F04-electricity-apr2023.txt
  -> Medium confidence | 1 flag(s): MISSING_FIELD:...
Processing: invoice-F06-gas-jan-feb-2023.txt
  -> Medium confidence | 1 flag(s): ...

Output written to: parsed-invoices.csv
Records processed: 5
Confidence: High=3  Medium=2  Low=0
```

## Extracted Fields

| Field | Description |
|-------|-------------|
| `facility_id` | Lumora facility code (F01–F09) |
| `facility_name` | Facility name as stated on the invoice |
| `country` | Country of the facility |
| `energy_type` | `electricity` / `natural_gas` / `diesel` / `other` |
| `quantity` | Consumption value as a plain number |
| `unit` | Unit as stated on the invoice (kWh, MWh, m3, GJ, litres) |
| `billing_period_start` | ISO 8601 date (YYYY-MM-DD) |
| `billing_period_end` | ISO 8601 date (YYYY-MM-DD) |
| `cost` | Total invoice amount, VAT-inclusive where available |
| `currency` | ISO 4217 code (EUR, VND, MXN, etc.) |
| `supplier` | Energy supplier name |
| `confidence_score` | High / Medium / Low |
| `anomaly_flags` | Semicolon-separated anomaly codes (empty if none) |
| `extraction_notes` | Model's note on assumptions or data quality concerns |
| `source_file` | Source invoice filename |

## Confidence Scoring

| Score | Criteria |
|-------|----------|
| **High** | All required fields extracted; no anomaly flags |
| **Medium** | 1–2 fields missing, OR only non-critical anomalies present |
| **Low** | 3+ fields missing, OR a critical anomaly flag is raised |

Critical anomaly types that force a Low score: `MISSING_CRITICAL_FIELD`, `QUANTITY_OUT_OF_RANGE`, `UNIT_MISMATCH`.

## Anomaly Detection

Five anomaly types are checked for each record:

| Code | Trigger |
|------|---------|
| `MISSING_CRITICAL_FIELD` | Core field (facility_id, energy_type, quantity, unit, billing period) is null |
| `MISSING_FIELD` | Non-critical field (cost, currency, supplier) is null |
| `QUANTITY_OUT_OF_RANGE` | Normalised value is >10× expected maximum or <10% of expected minimum for the facility type |
| `UNIT_MISMATCH` | Value is outside the expected range but would be in range with a common unit substitution (e.g., kWh vs MWh) |
| `BILLING_PERIOD_OVERLAP` | Billing period overlaps with a previously processed invoice for the same facility |
| `BILLING_PERIOD_GAP` | More than 5 days between consecutive invoice periods for the same facility |

Expected quantity ranges are defined per facility type (office, manufacturing, warehouse) and energy type. Electricity and gas values are normalised to kWh for comparison. Diesel remains in litres.

## Prompt Engineering

The extraction prompt applies three techniques from `CLAUDE.md`:

**1. Role and output format specification**
The system prompt instructs Claude to act as a GHG accounting data extraction agent and specifies the exact JSON schema — field names, types, and handling rules for ambiguous inputs (reactive vs active energy, quarterly billing periods, European decimal formats).

**2. Few-shot example**
A worked example (invoice text → expected JSON output) is embedded in the system prompt before any invoice is processed. This reduces hallucination on unit handling, date normalisation, and cost field selection (pre-tax vs VAT-inclusive).

**3. Prompt caching**
The system prompt (including the few-shot example) is marked with `cache_control: ephemeral`. Because the system prompt is identical for every invoice call in a batch, it is read from cache for invoices 2–5, reducing both API latency and token cost. This is the standard pattern for batch document processing with the Anthropic API.

## Simulated Invoices

The five invoices in `invoices/` are designed to reflect the document variability across Lumora's real facility portfolio:

| File | Facility | Energy Type | Challenge |
|------|----------|-------------|-----------|
| `invoice-F01-electricity-jan2023.txt` | Amsterdam HQ (F01) | Electricity — EUR, kWh | Clean reference case; Dutch format |
| `invoice-F02-gas-q1-2023.txt` | Eindhoven Mfg (F02) | Natural gas — EUR, m³ | Unit requires conversion; quarterly billing |
| `invoice-F02-diesel-q1-2023.txt` | Eindhoven Mfg (F02) | Diesel — EUR, litres | Multiple delivery lines; fleet fuel receipt format |
| `invoice-F04-electricity-apr2023.txt` | HCMC Mfg (F04) | Electricity — VND, kWh | Mixed Vietnamese/English; reactive power reading alongside active |
| `invoice-F06-gas-jan-feb-2023.txt` | Monterrey Mfg (F06) | Natural gas — MXN, GJ | Non-standard unit; two-month billing period; European decimal format |

## GHG Inventory Workflow Integration

This parser is the first stage of the Scope 1 and 2 data pipeline:

```
Raw invoices (PDF / text)
        │
        ▼
  receipt-parser/parser.py         ← This script
        │
        ▼
  parsed-invoices.csv              ← Structured activity data with quality flags
        │
        ▼
  Emission factor application      ← GHG Protocol factors (DEFRA, EPA eGRID, IEA, IPCC AR6)
        │
        ▼
  lumora-ghg-inventory.csv         ← Final GHG inventory
```

The `quantity`, `unit`, and `energy_type` fields feed directly into emission factor application. The `confidence_score` and `anomaly_flags` fields propagate data quality information through to the final inventory, supporting the tiered confidence scoring (primary / secondary / estimated) required under GHG Protocol and CSRD ESRS E1.

Any record with a `Low` confidence score or a `MISSING_CRITICAL_FIELD` flag must be resolved before emission factors are applied. Records flagged with `QUANTITY_OUT_OF_RANGE` or `UNIT_MISMATCH` require manual verification against the source document.

---

*Part of the AI-Augmented Sustainability & Climate Risk Portfolio | Taylor Black | github.com/taybeee/climate-portfolio*
