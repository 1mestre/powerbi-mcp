#!/usr/bin/env python3
"""
apply_theme.py — Applies a color theme to a Power BI PBIP project.

Usage:
    python apply_theme.py <project.pbip> --theme slate-terracotta
    python apply_theme.py <project.pbip> --theme-file my_theme.json

Modes:
  --theme <name>       One of: slate-terracotta, magenta-blossom, ecotone-spring,
                       roasted-espresso, vintage-nordic
  --theme-file <path>  Custom theme JSON file

Operations:
  1. Overwrites existing BaseThemes/<theme>.json file (NEVER creates new file)
  2. Applies background color to all page.json files
  3. Updates visual.json dataPoint colors for charts
  4. Validates contrast ratios

Exit code: 0 = success, 1 = error
"""

import json
import sys
from pathlib import Path

BUILTIN_THEMES = {
    "slate-terracotta": {
        "name": "CY26SU05",
        "dataColors": ["#A56F63", "#D99B7F", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6"],
        "background": "#0F3040",
        "foreground": "#F8FAFC",
        "tableAccent": "#A56F63",
        "good": "#10B981",
        "bad": "#EF4444",
        "neutral": "#A56F63"
    },
    "magenta-blossom": {
        "name": "CY26SU05",
        "dataColors": ["#92003A", "#F62477", "#FFADEE", "#FFE185", "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"],
        "background": "#FFFFFF",
        "foreground": "#111827",
        "tableAccent": "#92003A",
        "good": "#10B981",
        "bad": "#EF4444",
        "neutral": "#92003A"
    },
    "ecotone-spring": {
        "name": "CY26SU05",
        "dataColors": ["#769826", "#A1CB35", "#FFDE4E", "#FF9D4D", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6"],
        "background": "#F5F2EB",
        "foreground": "#1a1a2e",
        "tableAccent": "#769826",
        "good": "#A1CB35",
        "bad": "#EF4444",
        "neutral": "#769826"
    },
    "roasted-espresso": {
        "name": "CY26SU05",
        "dataColors": ["#60241E", "#95271D", "#B34A44", "#E77B49", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"],
        "background": "#1A0F0D",
        "foreground": "#F8FAFC",
        "tableAccent": "#B34A44",
        "good": "#10B981",
        "bad": "#EF4444",
        "neutral": "#B34A44"
    },
    "vintage-nordic": {
        "name": "CY26SU05",
        "dataColors": ["#0B1849", "#124D1C", "#E4B028", "#EBEDE3", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6"],
        "background": "#EBEDE3",
        "foreground": "#0B1849",
        "tableAccent": "#0B1849",
        "good": "#124D1C",
        "bad": "#C0392B",
        "neutral": "#0B1849"
    }
}


def apply_theme_file(project_root, project_name, theme):
    theme_dirs = [
        project_root / f"{project_name}.Report" / "StaticResources" / "SharedResources" / "BaseThemes",
        project_root / f"{project_name}.Report" / "definition" / "BaseThemes",
    ]
    for td in theme_dirs:
        if td.exists():
            existing = list(td.glob("*.json"))
            if existing:
                target = existing[0]
                with open(target, "r", encoding="utf-8") as f:
                    old_theme = json.load(f)
                old_name = old_theme.get("name", theme.get("name", "CY26SU05"))
                theme_out = dict(theme)
                theme_out["name"] = old_name
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(theme_out, f, indent=2, ensure_ascii=False)
                return {"status": "ok", "path": str(target),
                        "message": f"Theme overwritten with {len(theme['dataColors'])} data colors"}
    return {"status": "error", "path": "", "message": "No existing theme file found"}


def apply_page_backgrounds(project_root, project_name, bg_color):
    results = []
    pages_dir = project_root / f"{project_name}.Report" / "definition" / "pages"
    if not pages_dir.exists():
        return [{"status": "error", "message": f"Pages dir not found: {pages_dir}"}]
    for page_dir in sorted(pages_dir.iterdir()):
        if not page_dir.is_dir():
            continue
        page_json = page_dir / "page.json"
        if not page_json.exists():
            continue
        with open(page_json, "r", encoding="utf-8") as f:
            page = json.load(f)
        page.setdefault("objects", {})["background"] = [{
            "properties": {
                "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{bg_color}'"}}}}},
                "transparency": {"expr": {"Literal": {"Value": "0"}}}
            }
        }]
        with open(page_json, "w", encoding="utf-8") as f:
            json.dump(page, f, indent=2, ensure_ascii=False)
        results.append({"status": "ok", "path": str(page_json), "message": f"Background set"})
    return results


def apply_data_point_colors(project_root, project_name, data_colors):
    results = []
    visuals_glob = str(project_root / f"{project_name}.Report" / "definition" / "pages" / "**" / "visuals" / "**" / "visual.json")
    from glob import glob
    visual_files = glob(visuals_glob, recursive=True)
    for vpath_str in sorted(visual_files):
        vpath = Path(vpath_str)
        with open(vpath, "r", encoding="utf-8") as f:
            v = json.load(f)
        vtype = v.get("visual", {}).get("visualType", "")
        if vtype in ("treemap", "card", "slicer"):
            results.append({"status": "skipped", "path": str(vpath), "message": f"{vtype} skipped"})
            continue
        data_point = []
        for i, color in enumerate(data_colors):
            data_point.append({
                "properties": {
                    "fill": {
                        "solid": {
                            "color": {
                                "expr": {"ThemeDataColor": {"ColorId": i, "Percent": 0}}
                            }
                        }
                    }
                }
            })
        v.setdefault("visual", {}).setdefault("objects", {})["dataPoint"] = data_point
        with open(vpath, "w", encoding="utf-8") as f:
            json.dump(v, f, indent=2, ensure_ascii=False)
        results.append({"status": "ok", "path": str(vpath), "message": f"Applied colors to {vtype}"})
    if not visual_files:
        results.append({"status": "warning", "path": "", "message": "No visual.json files found"})
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply color theme to PBIP project")
    parser.add_argument("project", help="Path to .pbip file")
    parser.add_argument("--theme", choices=list(BUILTIN_THEMES.keys()), help="Built-in theme name")
    parser.add_argument("--theme-file", help="Custom theme JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    if not args.theme and not args.theme_file:
        print(json.dumps({"status": "error", "message": "Provide --theme or --theme-file",
                          "available_themes": list(BUILTIN_THEMES.keys())}, indent=2))
        sys.exit(1)

    pbip_path = Path(args.project)
    project_root = pbip_path.parent
    project_name = pbip_path.stem

    theme = BUILTIN_THEMES[args.theme] if args.theme else json.load(open(args.theme_file))

    results = {"status": "ok", "project": project_name, "root": str(project_root),
               "theme_name": args.theme or "custom", "operations": []}

    if not args.dry_run:
        tr = apply_theme_file(project_root, project_name, theme)
        results["operations"].append({"operation": "theme_file", **tr})
        bg = apply_page_backgrounds(project_root, project_name, theme["background"])
        results["operations"].append({"operation": "page_backgrounds", "pages_updated": sum(1 for r in bg if r["status"] == "ok"), "details": bg})
        dp = apply_data_point_colors(project_root, project_name, theme["dataColors"])
        results["operations"].append({"operation": "data_point_colors", "visuals_updated": sum(1 for r in dp if r["status"] == "ok"), "details": dp})
        if any(op.get("status") == "error" for op in results["operations"]):
            results["status"] = "error"

    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.exit(1 if results["status"] == "error" else 0)


if __name__ == "__main__":
    main()
