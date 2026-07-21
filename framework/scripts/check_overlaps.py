#!/usr/bin/env python3
"""check_overlaps.py — Detects overlapping visuals in PBIR reports."""

import json, sys
from pathlib import Path
from glob import glob

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: check_overlaps.py <project.pbip>"}))
        sys.exit(1)
    
    pbip_path = Path(sys.argv[1])
    if not pbip_path.exists() and pbip_path.suffix != ".pbip":
        found = list(Path(".").rglob("*.pbip"))
        if not found:
            print(json.dumps({"status": "error", "message": "No .pbip found"}))
            sys.exit(1)
        pbip_path = found[0]
    
    pname = pbip_path.stem
    report_dir = pbip_path.parent / f"{pname}.Report"
    visuals = []
    
    for vpath_str in sorted(glob(str(report_dir / "definition" / "pages" / "**" / "visuals" / "**" / "visual.json"), recursive=True)):
        vpath = Path(vpath_str)
        with open(vpath) as f:
            v = json.load(f)
        pos = v.get("position", {})
        vis = v.get("visual", {})
        visuals.append({
            "name": v.get("name", vpath.parent.name),
            "type": vis.get("visualType", "unknown"),
            "x": pos.get("x", 0), "y": pos.get("y", 0),
            "w": pos.get("width", 0), "h": pos.get("height", 0),
            "path": str(vpath)
        })
    
    issues = []
    # Overlap check
    for i, a in enumerate(visuals):
        for j, b in enumerate(visuals):
            if i >= j: continue
            xo = not (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"])
            yo = not (a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])
            if xo and yo:
                issues.append({"severity": "error", "type": "overlap",
                               "message": f"'{a['name']}' overlaps '{b['name']}'"})
    
    # Boundary check
    for v in visuals:
        if v["x"] + v["w"] > 1280:
            issues.append({"severity": "error", "type": "beyond_width",
                           "message": f"'{v['name']}' exceeds page width"})
        if v["h"] <= 0:
            issues.append({"severity": "error", "type": "zero_height",
                           "message": f"'{v['name']}' has zero height"})
        if v["type"] == "card" and v["h"] < 90:
            issues.append({"severity": "warning", "type": "kpi_height",
                           "message": f"KPI '{v['name']}' height {v['h']}px < 90px"})
        if v["type"] == "slicer" and v["h"] < 85:
            issues.append({"severity": "warning", "type": "slicer_height",
                           "message": f"Slicer '{v['name']}' height {v['h']}px < 85px"})
    
    errors = [i for i in issues if i["severity"] == "error"]
    result = {
        "status": "ok" if not errors else "error",
        "total_visuals": len(visuals),
        "total_issues": len(issues),
        "errors": len(errors),
        "issues": issues
    }
    print(json.dumps(result, indent=2))
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
