---
name: powerbi-pbir-troubleshooting
description: Operational traps, UTF-8 BOM encoding fixes, slicer orientation values, PBID rewrite behaviors, theme switching traps, and Python JSON manipulation templates.
---

# Power BI PBIR Operational Traps & Troubleshooting Skill

Use this skill when debugging errors in Power BI Desktop, fixing visual load crashes, handling JSON serialization issues, or inspecting PBIR runtime behaviors.

---

## 1. File Encoding & JSON Manipulation Fixes

### 1.1 UTF-8 WITHOUT BOM (CRITICAL FOR PBIP LOAD)
Power BI Project (PBIP) requires ALL JSON files to be **UTF-8 encoded WITHOUT Byte Order Mark (BOM)**. PowerShell 5.1 `Set-Content -Encoding UTF8` adds a BOM, which causes PBID to crash on open with: *"Only text with UTF8 encoding without BOM is supported. Detected BOM: 'UTF-8'"*.
**Fix:** Use .NET directly in PowerShell:
```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
```

### 1.2 Use Python for JSON Manipulation (CRITICAL)
PowerShell `ConvertFrom-Json` / `ConvertTo-Json` serializes nested hashtables as `"System.Collections.Hashtable"` strings, breaking PBIR's `expr.Literal.Value` structure. **Always use Python** for `visual.json` manipulation:

```python
import json

path = "Report/definition/pages/page_guid/visuals/vis_guid/visual.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Modify data cleanly...

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

---

## 2. Slicer & Chart Specific Fixes

### 2.1 Slicer Orientation Values
Slicer items require explicit `orientation` to show items. Power BI rewrites invalid or missing orientation to `"properties": {}` (no items render):
- `"0"` = vertical list (multi-row)
- `"1"` = horizontal (items arranged left-to-right in a single bar - best for full-width filters)
- `"2"` = responsive dropdown (auto-collapse)

**Fix:** Set `orientation: "1"` for filter bars:
```json
"items": [
  {
    "properties": {
      "orientation": { "expr": { "Literal": { "Value": "1" } } },
      "singleSelect": { "expr": { "Literal": { "Value": "false" } } }
    }
  }
]
```

### 2.2 Slicer Values Role Requirement
`pbir-cli` validation warns: `slicer missing 'Values' role -- visual will not render without it`. This applies to `pbir-cli` created slicers. However, PBID-internal slicers (created via UI) use `Group` without issues. The `Values` role is only needed when creating via `pbir-cli`.

### 2.3 Donut/Pie Charts: Start with Minimal Objects
Donut and pie charts with explicit `objects.legend` and `objects.labels` can fail to render in schema 1.0.0. **Fix:** Start with `"objects": {}` and schema `2.10.0`. Add legend/labels styling only after the chart renders with data.

### 2.4 NO `dataPoint` on Treemap
Treemaps use the theme's `dataColors` palette across all categories automatically. Adding `objects.dataPoint` with a single `ThemeDataColor` overrides all rectangles to one color. Using `ColorId: 0` sets them to the **background color** (`#F7F5F2`), making them invisible.
**Fix:** Do NOT include `dataPoint` in treemap objects. Use `"objects": {}`.

### 2.6 Multi-Color Bar Charts Enforcement (`showAllDataPoints: true`)
When configuring a `barChart` or `columnChart`, Power BI Desktop defaults to rendering all bars with a single monochrome color from the theme. Deleting `dataPoint` alone does NOT automatically color each category bar differently.

**Fix:** You MUST explicitly set `"showAllDataPoints": { "expr": { "Literal": { "Value": "true" } } }` inside `objects.dataPoint` to force Power BI to apply the distinct colors from the active theme's `dataColors` palette to each individual bar:

```json
"objects": {
  "dataPoint": [
    {
      "properties": {
        "showAllDataPoints": {
          "expr": { "Literal": { "Value": "true" } }
        }
      }
    }
  ]
}
```

### 2.5 Slicer Responsive Collapse Trap (Full-Width Filter Bars)

**Symptom:** A slicer configured with `responsive: true` and `orientation: "1"` (horizontal) collapses into a vertical search-list mode showing only the column name (e.g., `main_category`) and 1–2 items below it when the container height is ≤ 50 px. The slicer appears cut off and non-interactive.

**Root cause:** `responsive: true` + small height → Power BI ignores the `orientation` value entirely and forces a compressed search/list mode. The `orientation` property is only respected when `responsive` is `false`.

**Orientation reference:**

| Value | Mode | When to use |
|-------|------|-------------|
| `"0"` | Vertical list (multi-row) | Sidebars with ample vertical space |
| `"1"` | Horizontal tiles | ONLY with `responsive: false` AND height ≥ 80 px |
| `"2"` | Dropdown (collapsible) | **ALWAYS use for compact full-width filter bars** |

**Fix for Horizontal Button/Tile Slicers (`orientation: "1"`):**
To render interactive horizontal filter buttons (like the Amazon category button filter bar):
- Set `orientation: "1"` in `items`
- Set `general.responsive: false` (CRITICAL: if true, Power BI forces collapse into vertical list)
- Ensure container height is **at least `85px`** so tiles render fully without text clipping
- Set `header.show: false` and `visualContainerObjects.title.show: false` to maximize button space
- Set `items.selectedColor` to a glowing accent (e.g. `#FF9E2C` / Terracota) for active selection visual feedback

**Fix for Compact Dropdown Slicers (`orientation: "2"`):**
If vertical space is strictly limited (height ≤ 55px), **ALWAYS use `orientation: "2"` (dropdown)**. Attempting to use `orientation: "1"` (horizontal tiles) in narrow vertical spaces causes Power BI to render checkboxes vertically, leading to extreme visual overlapping with KPI cards below.

> [!WARNING]
> **Layout Overlap Trap:** If you switch a slicer from `orientation: "2"` to `orientation: "1"` without expanding the canvas height and pushing down all lower visual blocks (`y` coordinates), the slicer will visually bleed over and obscure the KPI cards below it. Always use `orientation: "2"` dropdowns for top filter bars unless the entire canvas grid is explicitly re-architected with vertical gaps ≥ 35px.

**Correct template — Horizontal Tile / Button Slicer:**
```json
"objects": {
  "general": [{
    "properties": {
      "responsive": { "expr": { "Literal": { "Value": "false" } } }
    }
  }],
  "header": [{
    "properties": {
      "show": { "expr": { "Literal": { "Value": "false" } } }
    }
  }],
  "items": [{
    "properties": {
      "orientation": { "expr": { "Literal": { "Value": "1" } } },
      "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } } } },
      "background": { "solid": { "color": { "expr": { "Literal": { "Value": "'#1A2A36'" } } } } },
      "selectedColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#FF9E2C'" } } } } },
      "singleSelect": { "expr": { "Literal": { "Value": "false" } } }
    }
  }]
}
```

**To hide the container title**, set this in `visualContainerObjects` (sibling of `objects` inside the `visual` block):
```json
"visualContainerObjects": {
  "title": [{
    "properties": {
      "show": { "expr": { "Literal": { "Value": "false" } } }
    }
  }]
}
```

---

## 3. Visual Creation & PBID Engine Behaviors

### 3.1 Use `pbir add visual` Instead of Manual JSON (CRITICAL)
Manually creating `visual.json` files — even with correct structure, projections, and objects — may result in visuals that **pass pbir-cli validation but do not render in PBID**. The root cause is that PBID initializes visuals through its UI pipeline, and manually added files bypass this.

**Solution:** Use `pbir add visual` to create new visuals. This generates correct JSON with PBID-compatible structure (proper `queryRef`, `nativeQueryRef`, `field` objects, schema version). After creation, add styling objects (legend, labels, header, items) via script.

**Workflow:**
1. Close PBID (`taskkill /IM PBIDesktop.exe /F`)
2. `pbir add visual <type> "$page" -n "name" -t "Title" -x X -y Y -w W -h H -d "Role:table.field"`
3. Add `objects` for styling via Python script
4. Reopen PBID

### 3.2 PBIR Role Names Differ from PBID Internal Names (CRITICAL)
PBID writes `Group` (slicers) and `Legend` (donut) internally, but the PBIR schema uses different role names. When creating visuals via `pbir add visual`, use the **schema roles**:

| Visual | PBID Internal | PBIR Schema (pbir-cli) |
|--------|--------------|----------------------|
| slicer | `Group` | `Values` |
| donutChart | `Legend` | `Category` |
| donutChart | `Category` (empty) | `Category` (empty) |
| donutChart | `Y` (empty) | `Y` (empty) |

**pbir-cli add command examples:**
```bash
# Slicer
pbir add visual slicer "$page" -n "name" -t "Title" -x 15 -y 15 -w 400 -h 110 -d "Values:table.column"

# Donut
pbir add visual donutChart "$page" -n "name" -t "Title" -x 855 -y 265 -w 410 -h 290 -d "Category:table.column" -d "Y:table.Measure"
```

### 3.3 pbir-cli TopN Filter Command
```bash
pbir add filter amazon_clean product_name \
  -v "Report/Page/Visual.Visual" \
  --type TopN --direction Top \
  --by-table amazon_clean --by-field "Total Revenue" \
  --n 5
```

### 3.4 Power BI Rewrites `visual.json` on Open
Power BI Desktop automatically upgrades `visual.json` schema from `1.0.0` to `2.10.0` and strips invalid properties on load. If a visual file is NOT rewritten (stays at `1.0.0` schema), it means Power BI FAILED to load it — the JSON has a structural error. **Debug method:** After opening PBID, check which visual files remained at `1.0.0` — those are the broken ones.

---

## 4. Root Property Errors & Naming Rules

### 4.1 PBID Errors for Invalid Root Properties
PBID reports these errors when root-level properties exist that shouldn't:
- `Se ha incluido una propiedad 'visualContainerObjects' adicional en la propiedad root` → Move `visualContainerObjects` INSIDE the `visual` object.
- `Se ha incluido una propiedad 'displayArea' adicional en la propiedad root de page.json` → Remove root-level `displayArea` from `page.json`.

### 4.2 `queryRef` / `nativeQueryRef` with Spaces
Measures or columns with spaces use dot-notation without brackets:
```json
"queryRef": "amazon_clean.Total Products",
"nativeQueryRef": "Total Products"
```

---

## 5. Theme Switching Traps (CRITICAL)

Switching a PBIR report theme programmatically (e.g., from `DarkNavy` to `SlateAndTerracotta`) involves 4 silent failure modes. All 4 MUST be addressed or the new theme will partially apply — layout changes but colors, backgrounds, and chart series remain from the old theme.

### 5.1 Trap 1 — Theme Cache Invalidation

PBID caches the active theme in `cache.abf` inside `.SemanticModel/.pbi/`. If this file exists when the report is opened after a theme change, PBID reads colors from cache and ignores the new theme JSON entirely.

**ALWAYS delete `cache.abf` before reopening PBID after any theme change:**
```python
import os

cache_path = r"MyReport.SemanticModel\.pbi\cache.abf"
if os.path.exists(cache_path):
    os.remove(cache_path)
    print("cache.abf deleted")
```

### 5.2 Trap 2 — New Theme File Name Not Resolved

If you create a NEW theme file (e.g., `SlateAndTerracotta.json`) and reference it in `report.json`, PBID may silently fall back to the default theme or the previous theme. PBID's theme resolver has issues resolving theme names that were never previously registered in the report session.

**NEVER create a new theme file. ALWAYS overwrite the existing theme file in `definition/BaseThemes/`**, keeping the same filename and the same `"name"` field inside the JSON. Only replace the color values:

```python
import json

theme_path = r"MyReport.Report\definition\BaseThemes\DarkNavy.json"

with open(theme_path, "r", encoding="utf-8") as f:
    theme = json.load(f)

# Replace colors IN PLACE — do NOT rename the file or change theme["name"]
theme["dataColors"] = [
    "#C0392B", "#E67E22", "#F1C40F",
    "#27AE60", "#2980B9", "#8E44AD",
    "#16A085", "#D35400"
]
theme["background"] = "#1C2B3A"
theme["foreground"] = "#ECF0F1"

with open(theme_path, "w", encoding="utf-8") as f:
    json.dump(theme, f, indent=2, ensure_ascii=False)
```

### 5.3 Trap 3 — `dataColors` Do Not Propagate to Pre-Rendered Charts

Charts that were previously saved while a different theme was active have their series colors baked into `visual.json` under `objects.dataPoint`. The new theme's `dataColors` palette does NOT override these explicit per-series color assignments.

**MUST force series colors explicitly in each chart's `visual.json`:**
```python
import json, glob, os

DATA_COLORS = [
    "#C0392B", "#E67E22", "#F1C40F",
    "#27AE60", "#2980B9", "#8E44AD"
]

visual_files = glob.glob(
    r"MyReport.Report\definition\pages\**\visuals\**\visual.json",
    recursive=True
)

for vpath in visual_files:
    with open(vpath, "r", encoding="utf-8") as f:
        v = json.load(f)

    vtype = v.get("visual", {}).get("visualType", "")
    # Skip visuals that must NOT have dataPoint (e.g. treemap — see §2.4)
    if vtype in ("treemap",):
        continue

    data_point = []
    for i, color in enumerate(DATA_COLORS):
        data_point.append({
            "id": {"$id": str(i)},
            "properties": {
                "fill": {
                    "solid": {"color": {"expr": {"Literal": {"Value": f"'{color}'"}}}}
                }
            }
        })

    v.setdefault("visual", {}).setdefault("objects", {})["dataPoint"] = data_point

    with open(vpath, "w", encoding="utf-8") as f:
        json.dump(v, f, indent=2, ensure_ascii=False)

print(f"Patched {len(visual_files)} visual files")
```

### 5.4 Trap 4 — Canvas Background Requires `page.json` Override

`visualStyles.page.*.background` inside the theme JSON is NOT sufficient to change the canvas background color. PBID ignores that key for the canvas. The background MUST be set directly in each page's `page.json`:

```python
import json, glob

BG_COLOR = "#1C2B3A"  # Must match theme["background"]

page_files = glob.glob(
    r"MyReport.Report\definition\pages\**\page.json",
    recursive=True
)

for ppath in page_files:
    with open(ppath, "r", encoding="utf-8") as f:
        page = json.load(f)

    page.setdefault("objects", {})["background"] = [
        {
            "properties": {
                # NOTE: NO 'show' property here — it causes a schema validation error in page.json
                # 'show' is only valid in visualContainerObjects, NOT in page-level objects
                "color": {
                    "solid": {
                        "color": {"expr": {"Literal": {"Value": f"'{BG_COLOR}'"}}}
                    }
                },
                "transparency": {"expr": {"Literal": {"Value": "0"}}}
            }
        }
    ]

    with open(ppath, "w", encoding="utf-8") as f:
        json.dump(page, f, indent=2, ensure_ascii=False)

print(f"Background set in {len(page_files)} pages")
```

### 5.6 Trap 5 — `show` Is INVALID in `page.json` background (Schema Error)

Power BI validates `page.json` against a strict JSON schema. The `background` property inside `page.json → objects` does **NOT** accept a `show` field. Including it causes an immediate load error:

> *"Se ha incluido una propiedad 'show' adicional en la propiedad /objects/background/0/properties"*

This schema difference is a common mistake because `visualContainerObjects.background` in `visual.json` DOES accept `show`.

**Rule:** `page.json` background only accepts `color` and `transparency`. Never add `show`.

```json
// WRONG — causes schema validation error in page.json
"background": [{
  "properties": {
    "show": { "expr": { "Literal": { "Value": "true" } } },  // <- INVALID HERE
    "color": { ... }
  }
}]

// CORRECT — page.json background
"background": [{
  "properties": {
    "color": {
      "solid": { "color": { "expr": { "Literal": { "Value": "'#0F3040'" } } } }
    },
    "transparency": { "expr": { "Literal": { "Value": "0" } } }
  }
}]
```

| Context | `show` valid? | `color` valid? | `transparency` valid? |
|---|---|---|---|
| `page.json → objects.background` | **NO** — schema error | YES | YES |
| `visual.json → visualContainerObjects.background` | YES | YES | YES |



### 5.5 Safe Theme-Switch Checklist

Execute ALL steps in order. Skipping any step causes partial application:

| Step | Action | Why |
|------|--------|-----|
| 1 | `taskkill /IM PBIDesktop.exe /F` | MUST be closed before file edits |
| 2 | Delete `cache.abf` | Clears old theme from PBID cache |
| 3 | Overwrite existing theme JSON (same filename) | New filenames may not resolve |
| 4 | Set `page.json → objects.background` on every page | Theme JSON `visualStyles.background` is ignored |
| 5 | Set `visual.json → objects.dataPoint` on every chart | Baked-in colors override theme `dataColors` |
| 6 | Reopen PBID and verify all pages | Confirm colors, backgrounds, and chart series |

---

## 🔗 RELATED SKILLS & REPOSITORY FILES

- 🏠 **[powerbi-pbir-editor](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-editor/SKILL.md)** - Master Skill Hub
- 📊 **[powerbi-pbir-visuals-specs](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-visuals-specs/SKILL.md)** - Visual Types & JSON Schemas
- 🚀 **[launch.py](file:///C:/Users/Sebas/desktop-ssas-mcp/launch.py)** - Launcher script avoiding PYTHONPATH collision
- 🛠️ **[fix_tmdl_format.py](file:///C:/Users/Sebas/desktop-ssas-mcp/fix_tmdl_format.py)** - TMDL format string sanitizer
