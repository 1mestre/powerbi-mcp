#!/usr/bin/env python3
"""check_overlaps.py — Detects overlapping visuals and boundary errors per page in PBIR reports."""

import json, sys
from pathlib import Path
from glob import glob
from collections import defaultdict

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
    
    pages = defaultdict(list)
    total_visuals = 0
    
    for vpath_str in sorted(glob(str(report_dir / "definition" / "pages" / "**" / "visuals" / "**" / "visual.json"), recursive=True)):
        vpath = Path(vpath_str)
        page_id = vpath.parent.parent.parent.name
        with open(vpath, "r", encoding="utf-8") as f:
            v = json.load(f)
        pos = v.get("position", {})
        vis = v.get("visual", {})
        pages[page_id].append({
            "name": v.get("name", vpath.parent.name),
            "type": vis.get("visualType", "unknown"),
            "x": pos.get("x", 0), "y": pos.get("y", 0),
            "w": pos.get("width", 0), "h": pos.get("height", 0),
            "path": str(vpath),
            "page": page_id
        })
        total_visuals += 1
    
    issues = []
    
    # Overlap check per page
    for page_id, visuals in pages.items():
        if len(visuals) > 6:
            issues.append({
                "severity": "warning",
                "type": "page_overcrowded",
                "message": f"Page '{page_id}' has {len(visuals)} visuals (recommended max is 5-6 visuals per page)"
            })
        
        for i, a in enumerate(visuals):
            for j, b in enumerate(visuals):
                if i >= j: continue
                xo = not (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"])
                yo = not (a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])
                if xo and yo:
                    issues.append({
                        "severity": "error",
                        "type": "overlap",
                        "page": page_id,
                        "message": f"Page '{page_id}': Visual '{a['name']}' overlaps '{b['name']}'"
                    })
        
        # Boundary & height check per visual
        for v in visuals:
            if v["x"] + v["w"] > 1280:
                issues.append({
                    "severity": "error",
                    "type": "beyond_width",
                    "page": page_id,
                    "message": f"Page '{page_id}': Visual '{v['name']}' ends at x={v['x']+v['w']}px, exceeding page width (1280px)"
                })
            if v["y"] + v["h"] > 720:
                issues.append({
                    "severity": "error",
                    "type": "beyond_height",
                    "page": page_id,
                    "message": f"Page '{page_id}': Visual '{v['name']}' ends at y={v['y']+v['h']}px, exceeding page height (720px)"
                })
            if v["h"] <= 0:
                issues.append({
                    "severity": "error",
                    "type": "zero_height",
                    "page": page_id,
                    "message": f"Page '{page_id}': Visual '{v['name']}' has zero height"
                })
            if v["type"] == "card" and v["h"] < 90:
                issues.append({
                    "severity": "warning",
                    "type": "kpi_height",
                    "page": page_id,
                    "message": f"Page '{page_id}': KPI '{v['name']}' height {v['h']}px < 90px"
                })
            if v["type"] == "slicer" and v["h"] < 85:
                issues.append({
                    "severity": "warning",
                    "type": "slicer_height",
                    "page": page_id,
                    "message": f"Page '{page_id}': Slicer '{v['name']}' height {v['h']}px < 85px"
                })
    
    errors = [i for i in issues if i["severity"] == "error"]
    result = {
        "status": "ok" if not errors else "error",
        "total_pages": len(pages),
        "total_visuals": total_visuals,
        "total_issues": len(issues),
        "errors": len(errors),
        "issues": issues
    }
    print(json.dumps(result, indent=2))
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
