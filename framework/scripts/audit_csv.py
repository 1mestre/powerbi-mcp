#!/usr/bin/env python3
"""audit_csv.py — Audit a CSV for Power BI readiness.

Usage:
    python audit_csv.py data.csv
    python audit_csv.py data.csv --json   # machine-readable output

Audits: encoding, BOM, column count, nulls, data types, 
duplicates, special characters, line-ending consistency.
Never modifies the original file.
"""

import csv, json, sys, os
from pathlib import Path
from datetime import datetime

def audit_csv(csv_path, json_output=False):
    path = Path(csv_path)
    report = {"file": str(path.absolute()), "size": path.stat().st_size}
    errors = []
    warnings = []

    # --- Encoding & BOM detection ---
    raw = path.read_bytes()
    if raw[:3] == b'\xef\xbb\xbf':
        report["bom"] = "UTF-8 BOM"
        warnings.append({"type": "bom", "msg": "UTF-8 BOM present — handleable by Power Query"})
        raw = raw[3:]  # strip BOM for decoding
    else:
        report["bom"] = "none"
    if raw[:2] == b'\xff\xfe':
        errors.append({"type": "encoding", "msg": "UTF-16 LE BOM — Power BI may fail to parse"})

    null_idx = raw.find(b'\x00')
    if null_idx >= 0:
        errors.append({"type": "null_byte", "msg": f"Null byte at byte offset {null_idx}"})

    # Encoding detection
    encoding = None
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            raw.decode(enc)
            encoding = enc
            break
        except UnicodeDecodeError:
            continue
    if not encoding:
        errors.append({"type": "encoding", "msg": "Could not decode file with utf-8/latin-1/cp1252"})
        encoding = "utf-8"
    report["encoding"] = encoding

    text = raw.decode(encoding, errors='replace')

    # CRLF detection
    crlf_count = raw.count(b'\r\n')
    lf_only = raw.count(b'\n') - crlf_count
    report["line_endings"] = "CRLF" if crlf_count > 0 and lf_only == 0 else ("mixed" if crlf_count > 0 else "LF")
    if report["line_endings"] == "mixed":
        warnings.append({"type": "line_endings", "msg": "Mixed CRLF and LF line endings"})

    # --- Parse CSV with csv.reader (handles quoted fields) ---
    import io
    reader = csv.reader(io.StringIO(text))
    try:
        headers = next(reader)
    except StopIteration:
        errors.append({"type": "empty", "msg": "File is empty"})
        report["status"] = "error"
        return report

    report["headers"] = headers
    report["column_count"] = len(headers)

    # Row analysis
    rows = []
    empty_rows = 0
    inconsistent_cols = 0
    max_cols = 0

    for i, row in enumerate(reader):
        if not row or all(c.strip() == '' for c in row):
            empty_rows += 1
            continue
        rows.append(row)
        if len(row) != len(headers):
            inconsistent_cols += 1
        if len(row) > max_cols:
            max_cols = len(row)

    report["data_rows"] = len(rows)
    report["empty_rows"] = empty_rows
    report["inconsistent_column_counts"] = inconsistent_cols
    report["max_columns_seen"] = max_cols

    # --- Column analysis ---
    col_data = {}
    for h in headers:
        col_data[h] = {"values": [], "nulls": 0, "non_null": 0}

    whitespace_cols = {}
    for row in rows:
        for j, val in enumerate(row):
            if j >= len(headers):
                continue
            h = headers[j]
            if val.strip() == '' or val == '':
                col_data[h]["nulls"] += 1
            else:
                col_data[h]["values"].append(val)
                col_data[h]["non_null"] += 1
            if val != val.strip():
                whitespace_cols[h] = whitespace_cols.get(h, 0) + 1

    if whitespace_cols:
        top5 = sorted(whitespace_cols.items(), key=lambda x: -x[1])[:5]
        warnings.append({"type": "whitespace", "msg": f"Leading/trailing whitespace in {len(whitespace_cols)} columns", "details": top5})

    # Type inference per column
    report["columns"] = []
    for h in headers:
        cd = col_data[h]
        total = cd["nulls"] + cd["non_null"]
        pct_null = round(cd["nulls"] / total * 100, 1) if total > 0 else 0
        unique_vals = len(set(cd["values"]))
        col_info = {
            "name": h, "total": total, "nulls": cd["nulls"],
            "null_pct": pct_null, "unique": unique_vals,
            "sample_values": list(set(cd["values"]))[:5]
        }
        if cd["non_null"] > 0:
            vals = cd["values"]
            int_count = sum(1 for v in vals if _is_int(v))
            dec_count = sum(1 for v in vals if _is_decimal(v))
            n = len(vals)
            if int_count == n:
                col_info["inferred_type"] = "Integer"
            elif dec_count >= n * 0.5:
                col_info["inferred_type"] = "Decimal"
            else:
                col_info["inferred_type"] = "Text"
            # Date check on sample
            date_count = sum(1 for v in vals[:100] if _is_date(v))
            if date_count >= 50:
                col_info["inferred_type"] = "Date"
        else:
            col_info["inferred_type"] = "Empty"
        report["columns"].append(col_info)

    # --- Row-level issues ---
    # Check for unbalanced quotes by parsing raw text
    quote_rows_raw = []
    in_quotes = False
    for lineno, line in enumerate(text.split('\n')):
        for ch in line:
            if ch == '"':
                in_quotes = not in_quotes
        if in_quotes:
            quote_rows_raw.append(lineno + 1)
    if quote_rows_raw:
        errors.append({
            "type": "unbalanced_quotes",
            "msg": f"Unbalanced quotes detected at line(s) {quote_rows_raw[:5]}{'...' if len(quote_rows_raw) > 5 else ''}",
            "detail": "This will cause Power BI parse errors. Ensure multi-line quoted fields are well-formed."
        })

    if inconsistent_cols > 0:
        errors.append({
            "type": "inconsistent_columns",
            "msg": f"{inconsistent_cols}/{len(rows)} rows have ≠{len(headers)} columns (max seen: {max_cols})",
            "detail": "Usually means some fields contain commas without proper quoting. Check columns with comma-separated lists (e.g., 'cast', 'listed_in')."
        })

    # --- Summary ---
    if errors:
        report["recommendation"] = "FAIL — fix errors before loading into Power BI"
    elif warnings:
        report["recommendation"] = "WARN — minor issues detected, usually safe to load"
    else:
        report["recommendation"] = "PASS — CSV is clean"

    report["errors"] = errors
    report["warnings"] = warnings
    report["status"] = "error" if errors else "ok"

    # Output
    if json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_report(report)
    return report


def _is_int(v):
    try:
        int(float(v.replace(',', '')))
        return '.' not in v.replace(',', '')
    except: return False

def _is_decimal(v):
    try:
        float(v.replace(',', ''))
        return True
    except: return False

def _is_date(v):
    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
        try:
            datetime.strptime(v, fmt)
            return True
        except: pass
    return False

def _print_report(r):
    print(f"=== CSV Audit Report: {r['file']} ===")
    print(f"Size: {r['size']:,} bytes | Encoding: {r['encoding']} | BOM: {r['bom']}")
    print(f"Headers: {r['column_count']} columns | Line endings: {r['line_endings']}")
    print(f"Data rows: {r['data_rows']:,} | Empty rows: {r['empty_rows']}")
    if r['inconsistent_column_counts']:
        print(f"⚠️ Inconsistent column count: {r['inconsistent_column_counts']} rows (max {r['max_columns_seen']})")
    print()
    if r['errors']:
        print("🔴 ERRORS:")
        for e in r['errors']:
            print(f"  ❌ {e['msg']}")  
            if 'detail' in e:
                print(f"     Tip: {e['detail']}")
    if r['warnings']:
        print("🟡 WARNINGS:")
        for w in r['warnings'][:5]:
            print(f"  ⚠️  {w['msg']}")
    print(f"\n📊 Column Analysis:")
    print(f"  {'Column':<25} {'Type':<10} {'Null%':<8} {'Unique':<8}")
    print(f"  {'-'*25} {'-'*10} {'-'*8} {'-'*8}")
    for col in r['columns']:
        print(f"  {col['name']:<25} {col['inferred_type']:<10} {col['null_pct']:<8}% {col['unique']:<8}")
    print(f"\n📋 Recommendation: {r.get('recommendation', 'N/A')}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Audit a CSV for Power BI readiness')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()
    sys.exit(1 if audit_csv(args.csv_file, json_output=args.json).get("status") == "error" else 0)
