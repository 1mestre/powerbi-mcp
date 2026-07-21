#!/usr/bin/env python3
"""
fix_tmdl.py — Fixes common TMDL file issues in Power BI Semantic Models.

Usage:
    python fix_tmdl.py <file_or_directory> [--dry-run] [--verbose]

Fixes:
  1. CRLF (\\r\\n) -> LF (\\n) — CRLF causes InvalidLineType: Other
  2. Unquoted formatString -> double-quoted formatString
  3. Detects // comments on line 1 (must warn, not auto-fix)
  4. Removes trailing whitespace
  5. Removes UTF-8 BOM

Exit code: 0 = all good, 1 = uncorrectable errors found
"""

import json
import re
import sys
from pathlib import Path


def fix_crlf(content: bytes) -> tuple:
    if b"\r\n" in content:
        return content.replace(b"\r\n", b"\n"), True
    return content, False


def fix_bom(content: bytes) -> tuple:
    if content[:3] == b"\xef\xbb\xbf":
        return content[3:], True
    return content, False


def fix_format_strings(text: str) -> tuple:
    pattern = r'(formatString:\s*)(["\']?)([^"\'\n]+?)(["\']?)(\s*)$'
    count = 0

    def replacer(m):
        nonlocal count
        prefix = m.group(1)
        open_q = m.group(2)
        value = m.group(3).strip()
        close_q = m.group(4)
        trailing = m.group(5)
        if open_q == '"' and close_q == '"':
            return m.group(0)
        if open_q == "'" and close_q == "'":
            count += 1
            return f'{prefix}"{value}"{trailing}'
        if not open_q and not close_q:
            count += 1
            return f'{prefix}"{value}"{trailing}'
        return m.group(0)

    result = re.sub(pattern, replacer, text, flags=re.MULTILINE)
    return result, count


def fix_trailing_spaces(text: str) -> tuple:
    lines = text.split("\n")
    count = 0
    fixed = []
    for line in lines:
        stripped = line.rstrip()
        if stripped != line:
            count += 1
        fixed.append(stripped)
    return "\n".join(fixed), count


def check_line1_comment(text: str) -> list:
    lines = text.strip().split("\n")
    warnings = []
    if lines:
        first = lines[0].strip()
        if first.startswith("//"):
            warnings.append("Line 1 has '//' comment - move it AFTER 'model X {' declaration")
        if first.startswith("--"):
            warnings.append("Line 1 has '--' SQL-style comment - TMDL does not support this")
    return warnings


def process_file(path: Path, dry_run: bool = False) -> dict:
    result = {
        "path": str(path),
        "status": "ok",
        "corrections": [],
        "warnings": [],
        "errors": []
    }

    try:
        with open(path, "rb") as f:
            original = f.read()
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Cannot read: {e}")
        return result

    content = original
    corrections = []

    content, bom_fixed = fix_bom(content)
    if bom_fixed:
        corrections.append("Removed UTF-8 BOM")

    content, crlf_fixed = fix_crlf(content)
    if crlf_fixed:
        corrections.append("Converted CRLF to LF")

    text = content.decode("utf-8", errors="replace")
    result["warnings"].extend(check_line1_comment(text))

    text, fs_count = fix_format_strings(text)
    if fs_count > 0:
        corrections.append(f"Fixed {fs_count} unquoted formatString(s)")

    text, ts_count = fix_trailing_spaces(text)
    if ts_count > 0:
        corrections.append(f"Trimmed trailing whitespace on {ts_count} line(s)")

    new_content = text.encode("utf-8")

    if new_content != original:
        if not dry_run:
            with open(path, "wb") as f:
                f.write(new_content)
        result["corrections"] = corrections
        result["status"] = "fixed"
    else:
        result["status"] = "ok"

    return result


def find_tmdl_files(target: Path) -> list:
    if target.is_file() and target.suffix == ".tmdl":
        return [target]
    elif target.is_dir():
        return sorted(target.rglob("*.tmdl"))
    elif target.suffix == ".pbip":
        return sorted(target.parent.rglob("*.tmdl"))
    else:
        return sorted(Path(".").rglob("*.tmdl"))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix common TMDL file issues")
    parser.add_argument("target", nargs="?", default=".",
                        help=".tmdl file, directory, or .pbip project (default: .)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be fixed without modifying")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show details per file")
    args = parser.parse_args()

    target = Path(args.target)
    files = find_tmdl_files(target)

    if not files:
        print(json.dumps({
            "status": "error",
            "message": f"No .tmdl files found in: {target}",
            "files_checked": 0,
            "files_fixed": 0
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    results = []
    fixed_count = 0
    error_count = 0

    for f in files:
        r = process_file(f, dry_run=args.dry_run)
        results.append(r)
        if r["status"] == "fixed":
            fixed_count += 1
        elif r["status"] == "error":
            error_count += 1
        if args.verbose and (r["corrections"] or r["warnings"]):
            print(f"  [{r['status'].upper()}] {f.name}")
            for c in r["corrections"]:
                print(f"    + {c}")
            for w in r["warnings"]:
                print(f"    ! {w}")
            for e in r["errors"]:
                print(f"    x {e}")

    summary = {
        "status": "ok" if error_count == 0 else "error",
        "dry_run": args.dry_run,
        "files_checked": len(files),
        "files_fixed": fixed_count,
        "files_with_errors": error_count,
        "files": results
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
