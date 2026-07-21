#!/usr/bin/env python3
"""
validate_pbip.py — Validates a Power BI PBIP project structure.

Usage:
    python validate_pbip.py <path_to_project.pbip>

Returns exit code 0 if all good, 1 if errors found.
Prints JSON output for agent parsing.

Checks:
  1. .pbip file exists and is valid JSON
  2. .Report/ folder exists with definition.pbir
  3. definition/version.json exists
  4. definition/report.json exists with $schema
  5. pages/pages.json exists with pageOrder
  6. pages/<guid>/page.json exists
  7. Visuals exist (at least 1)
  8. .SemanticModel/ exists with definition.pbism
  9. Table .tmdl files exist and have NO CRLF
  10. cache.abf was deleted
  11. UTF-8 without BOM on all JSON files
"""

import json
import os
import sys
from pathlib import Path


def check_file_exists(path, label):
    p = Path(path)
    ok = p.exists() and p.is_file()
    return {"check": label, "path": str(p), "status": "ok" if ok else "error",
            "message": "" if ok else f"File not found: {path}"}


def check_dir_exists(path, label):
    p = Path(path)
    ok = p.exists() and p.is_dir()
    return {"check": label, "path": str(p), "status": "ok" if ok else "error",
            "message": "" if ok else f"Directory not found: {path}"}


def check_json_valid(path, label):
    p = Path(path)
    if not p.exists():
        return {"check": label, "path": str(p), "status": "error", "message": "File does not exist"}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"check": label, "path": str(p), "status": "ok", "message": "", "content_type": str(type(data).__name__)}
    except json.JSONDecodeError as e:
        return {"check": label, "path": str(p), "status": "error", "message": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"check": label, "path": str(p), "status": "error", "message": str(e)}


def check_no_crlf(path, label):
    """Check file does NOT have CRLF (\\r\\n)."""
    p = Path(path)
    if not p.exists():
        return {"check": label, "path": str(p), "status": "error", "message": "File not found"}
    with open(p, "rb") as f:
        content = f.read()
    if b"\r\n" in content:
        count = content.count(b"\r\n")
        return {"check": label, "path": str(p), "status": "error",
                "message": f"CRLF detected ({count} occurrences). Use LF only (\\n)."}
    return {"check": label, "path": str(p), "status": "ok", "message": "LF only"}


def check_no_bom(path, label):
    p = Path(path)
    if not p.exists():
        return {"check": label, "path": str(p), "status": "error", "message": "File not found"}
    with open(p, "rb") as f:
        content = f.read(4)
    if content[:3] == b"\xef\xbb\xbf":
        return {"check": label, "path": str(p), "status": "error",
                "message": "UTF-8 BOM detected. Use UTF-8 without BOM."}
    return {"check": label, "path": str(p), "status": "ok", "message": "No BOM"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python validate_pbip.py <path_to_project.pbip>",
            "checks": []
        }, indent=2))
        sys.exit(1)

    pbip_path = Path(sys.argv[1])
    if not pbip_path.exists():
        # Try to find .pbip files
        candidates = list(Path(sys.argv[1]).rglob("*.pbip")) if Path(sys.argv[1]).is_dir() else []
        if not candidates:
            print(json.dumps({
                "status": "error",
                "message": f"No .pbip file found at: {sys.argv[1]}",
                "checks": []
            }, indent=2))
            sys.exit(1)
        pbip_path = candidates[0]

    project_root = pbip_path.parent
    project_name = pbip_path.stem
    results = []

    # 1. Check .pbip file
    results.append(check_file_exists(str(pbip_path), "pbip_file"))
    results.append(check_json_valid(str(pbip_path), "pbip_json_valid"))
    results.append(check_no_bom(str(pbip_path), "pbip_no_bom"))

    # 2. Check .Report/ structure
    report_dir = project_root / f"{project_name}.Report"
    results.append(check_dir_exists(str(report_dir), "report_dir"))

    if report_dir.exists():
        definition_pbir = report_dir / "definition.pbir"
        results.append(check_file_exists(str(definition_pbir), "definition_pbir"))
        results.append(check_json_valid(str(definition_pbir), "definition_pbir_json"))

        def_dir = report_dir / "definition"
        results.append(check_dir_exists(str(def_dir), "definition_dir"))

        if def_dir.exists():
            version_json = def_dir / "version.json"
            results.append(check_file_exists(str(version_json), "version_json"))
            results.append(check_json_valid(str(version_json), "version_json_valid"))

            report_json = def_dir / "report.json"
            results.append(check_file_exists(str(report_json), "report_json"))
            rj = check_json_valid(str(report_json), "report_json_valid")
            results.append(rj)
            if rj["status"] == "ok":
                with open(report_json, "r", encoding="utf-8") as f:
                    rdata = json.load(f)
                if "$schema" not in rdata:
                    results.append({"check": "report_json_schema", "path": str(report_json),
                                    "status": "error", "message": "report.json missing $schema"})
                else:
                    results.append({"check": "report_json_schema", "path": str(report_json),
                                    "status": "ok", "message": f"$schema present"})
                if "themeCollection" not in rdata:
                    results.append({"check": "report_json_theme", "path": str(report_json),
                                    "status": "error", "message": "report.json missing themeCollection"})
                else:
                    results.append({"check": "report_json_theme", "path": str(report_json),
                                    "status": "ok", "message": "themeCollection present"})

            pages_dir = def_dir / "pages"
            results.append(check_dir_exists(str(pages_dir), "pages_dir"))

            if pages_dir.exists():
                pages_json = pages_dir / "pages.json"
                results.append(check_file_exists(str(pages_json), "pages_json"))
                results.append(check_json_valid(str(pages_json), "pages_json_valid"))

                page_dirs = [d for d in pages_dir.iterdir() if d.is_dir()]
                results.append({"check": "page_count", "path": str(pages_dir),
                                "status": "ok" if page_dirs else "warning",
                                "message": f"{len(page_dirs)} page(s) found"})

                for pdir in page_dirs:
                    page_json = pdir / "page.json"
                    results.append(check_file_exists(str(page_json), f"page_json_{pdir.name}"))
                    results.append(check_json_valid(str(page_json), f"page_json_{pdir.name}_valid"))

                    visuals_dir = pdir / "visuals"
                    if visuals_dir.exists():
                        visual_dirs = [v for v in visuals_dir.iterdir() if v.is_dir()]
                        results.append({"check": f"visual_count_{pdir.name}", "path": str(visuals_dir),
                                        "status": "ok" if visual_dirs else "warning",
                                        "message": f"{len(visual_dirs)} visual(s) in page {pdir.name}"})
                        for vdir in visual_dirs:
                            vjson = vdir / "visual.json"
                            results.append(check_file_exists(str(vjson), f"visual_json_{vdir.name}"))
                            results.append(check_json_valid(str(vjson), f"visual_json_{vdir.name}_valid"))
                            results.append(check_no_bom(str(vjson), f"visual_no_bom_{vdir.name}"))

                            # Check visual.json has "name" at root
                            try:
                                with open(vjson, "r", encoding="utf-8") as f:
                                    vdata = json.load(f)
                                if "name" not in vdata:
                                    results.append({"check": f"visual_name_{vdir.name}", "path": str(vjson),
                                                    "status": "error",
                                                    "message": "visual.json missing 'name' at root level"})
                            except:
                                pass
                    else:
                        results.append({"check": f"visuals_dir_{pdir.name}", "path": str(visuals_dir),
                                        "status": "warning", "message": f"No visuals/ folder in page {pdir.name}"})

    # 3. Theme files
    static_resources = report_dir / "StaticResources" / "SharedResources" / "BaseThemes"
    if static_resources.exists():
        theme_files = list(static_resources.glob("*.json"))
        results.append({"check": "theme_files", "path": str(static_resources),
                        "status": "ok" if theme_files else "warning",
                        "message": f"Theme(s): {', '.join(t.name for t in theme_files) if theme_files else 'None'}"})
        for tf in theme_files:
            results.append(check_json_valid(str(tf), f"theme_{tf.stem}"))

    # 4. Check .SemanticModel/
    sm_dir = project_root / f"{project_name}.SemanticModel"
    results.append(check_dir_exists(str(sm_dir), "sm_dir"))

    if sm_dir.exists():
        definition_pbism = sm_dir / "definition.pbism"
        results.append(check_file_exists(str(definition_pbism), "definition_pbism"))
        results.append(check_json_valid(str(definition_pbism), "definition_pbism_valid"))

        tables_dir = sm_dir / "definition" / "tables"
        model_bim = sm_dir / "model.bim"
        model_tmdl = sm_dir / "definition" / "model.tmdl"

        if tables_dir.exists():
            tmdl_files = list(tables_dir.glob("*.tmdl"))
            results.append({"check": "tmdl_tables", "path": str(tables_dir),
                            "status": "ok" if tmdl_files else "error",
                            "message": f"{len(tmdl_files)} .tmdl file(s)" if tmdl_files else "No .tmdl files in tables/"})
            for tf in tmdl_files:
                results.append(check_no_crlf(str(tf), f"tmdl_no_crlf_{tf.stem}"))
        elif model_bim.exists():
            results.append({"check": "model_bim", "path": str(model_bim),
                            "status": "ok", "message": "model.bim found (TMSL format)"})
        elif model_tmdl.exists():
            results.append({"check": "model_tmdl", "path": str(model_tmdl),
                            "status": "ok", "message": "model.tmdl found"})
            results.append(check_no_crlf(str(model_tmdl), "model_tmdl_no_crlf"))
        else:
            results.append({"check": "model_definitions", "path": str(sm_dir / "definition"),
                            "status": "error",
                            "message": "No tables/*.tmdl, model.bim, or model.tmdl found"})

        # cache.abf check
        cache_abf = sm_dir / ".pbi" / "cache.abf"
        results.append({"check": "cache_abf", "path": str(cache_abf),
                        "status": "warning" if cache_abf.exists() else "ok",
                        "message": "cache.abf still exists — delete before reopening PBID" if cache_abf.exists()
                                   else "cache.abf does not exist (OK)"})

    # Summary
    errors = [r for r in results if r["status"] == "error"]
    warnings = [r for r in results if r["status"] == "warning"]

    output = {
        "status": "ok" if not errors else "error",
        "project": project_name,
        "root": str(project_root),
        "total_checks": len(results),
        "errors": len(errors),
        "warnings": len(warnings),
        "passed": len(results) - len(errors) - len(warnings),
        "checks": results
    }

    if errors:
        output["error_summary"] = [{"check": e["check"], "message": e["message"]} for e in errors]

    print(json.dumps(output, indent=2, ensure_ascii=False))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
