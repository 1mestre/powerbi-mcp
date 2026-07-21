---
name: powerbi-csv-audit
description: Best practices and automated script for auditing CSV data before loading into Power BI. Detects unbalanced quotes, inconsistent columns, encoding issues, and data quality problems.
tags: [powerbi, csv, data-quality, audit, preflight]
---

# CSV Audit for Power BI

## When to Use This Skill
Load this skill when the user provides a CSV/Excel file for a Power BI dashboard and you need to:
1. Validate the file can be loaded without PBID errors
2. Detect data quality issues before suggesting the user load it
3. Diagnose "X rows loaded, Y errors" messages

## The Problem
Power BI Desktop reports parsing errors like "Cargar: 1 de las consultas cargadas contienen errores" or "Se cargaron X filas. Y errores." These are caused by structural CSV issues, not data content.

## Detection Order

### Step 1: Run the Audit Script
```bash
python <skill-path>/scripts/audit_csv.py <file.csv>
```

Look for these error types:

| Error | Meaning | Common Cause |
|-------|---------|-------------|
| `unbalanced_quotes` | A double-quote opens but never closes | Multi-line text field with line break inside quotes |
| `inconsistent_columns` | Row has different column count than header | A field contains commas but was not quoted (e.g., `cast` column with actor names) |
| `null_byte` | Binary zero in file | Corrupted export |
| `encoding_errors` | File not valid UTF-8 | Exported as Latin-1/Windows-1252 |

### Step 2: Present to User
```python
if errors:
    "❌ I found [N] issue(s) with the CSV that will cause Power BI errors:
     - [Error descriptions with line numbers]
     
    Recommendation: Re-export the CSV with proper quoting, or fix the affected rows."
```

### Step 3: Never Let PBID Load a Broken File
If `audit_csv.py` reports errors, DO NOT tell the user to load the file in PBID. The load will fail with the exact same errors. Fix the source CSV first.

## Common CSV Export Fixes

### Excel → CSV with Proper Quoting
1. File → Save As → CSV UTF-8 (Comma delimited) (*.csv)
2. NOT "CSV (Comma delimited)" — that uses ANSI encoding
3. In Mac Excel: File → Export → CSV UTF-8

### Database Export with Proper Quoting
1. SQL Server: Use `BCP` with `-c -t, -T` or SSIS with "Text qualified" = `"`
2. PostgreSQL: `COPY ... TO '/file.csv' WITH (FORMAT CSV, HEADER, ENCODING 'UTF8')`
3. MySQL: `SELECT ... INTO OUTFILE '/file.csv' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'`

## Fallback: Clean Programmatically
If the user cannot re-export, the orchestrator can:
1. Read raw bytes
2. Fix bad quoting by identifying field boundaries
3. Write a clean copy

But prefer re-export. Programmatic cleaning is fragile with large CSVs.

## Training Data: Real-World Case
The NETFLIX catalog CSV (8,807 rows, 19 columns) had:
- **2 lines with unbalanced quotes** (lines 8203, 8422) — the exact 2 errors PBID reported
- Fields with multi-row text in `description` column
### Diagnosis:
```python
in_quotes = False
for lineno, line in enumerate(text.split('\n')):
    for ch in line:
        if ch == '"': in_quotes = not in_quotes
    if in_quotes: print(f"Unbalanced at line {lineno+1}")
```

## Reference Files
This skill ships with supporting reference files for related PBIR/design topics:

| File | Content |
|------|---------|
| `references/dark-theme-contrast.md` | Dark theme text visibility, firstLevelElements, visual backgrounds |
| `references/pbir-pitfalls.md` | pbir CLI encoding bug, CRLF from MCP tools, golden rule clarifications |
| `references/bar-chart-color-rules.md` | Categorical vs temporal bar coloring in PBIR |
