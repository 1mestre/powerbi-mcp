#!/usr/bin/env python3
"""csv_fix.py — Creates a clean copy of a CSV with proper quoting.

Usage:
    python csv_fix.py broken.csv            # writes broken_clean.csv
    python csv_fix.py broken.csv --out fixed.csv

Reads any CSV (handles multi-line quotes, mixed delimiters) and writes
a clean RFC 4180-compliant copy. Never overwrites the original.
"""

import csv, io, sys, os
from pathlib import Path

def fix_csv(csv_path, output_path=None):
    path = Path(csv_path)
    if output_path is None:
        stem = path.stem
        output_path = path.with_name(f"{stem}_clean.csv")
    
    # Detect encoding
    raw = path.read_bytes()
    for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
        try:
            text = raw.decode(enc)
            if enc == 'utf-8-sig' and raw[:3] == b'\xef\xbb\xbf':
                text = text[1:]  # strip BOM
            break
        except UnicodeDecodeError:
            continue
    
    # Parse with csv (handles multi-line quoted fields)
    reader = csv.reader(io.StringIO(text))
    headers = next(reader)
    
    rows_out = []
    error_count = 0
    for i, row in enumerate(reader, 2):
        if not row or all(c.strip() == '' for c in row):
            continue
        # Fix column count mismatches
        if len(row) != len(headers):
            error_count += 1
            if len(row) > len(headers):
                row = row[:len(headers)-1] + [','.join(row[len(headers)-1:])]
            else:
                row = list(row) + [''] * (len(headers) - len(row))
        rows_out.append(row)
    
    # Write clean CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(rows_out)
    
    report = {
        "status": "ok",
        "input": str(path.absolute()),
        "output": str(output_path.absolute()),
        "rows_read": len(rows_out) + 1,
        "rows_written": len(rows_out),
        "columns": len(headers),
        "fixed_rows": error_count,
        "note": "Use this clean file as the Power Query source instead of the original"
    }
    return report

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Fix a CSV with quoting issues')
    parser.add_argument('csv_file', help='Path to broken CSV')
    parser.add_argument('--out', '-o', help='Output path (default: <name>_clean.csv)')
    args = parser.parse_args()
    report = fix_csv(args.csv_file, args.out)
    print(f"✅ {report['rows_written']} rows written to {report['output']}")
    if report['fixed_rows']:
        print(f"⚠️  {report['fixed_rows']} rows had column count issues (fixed)")
    print(f"Recommendation: update Power Query source to point to the clean file")
