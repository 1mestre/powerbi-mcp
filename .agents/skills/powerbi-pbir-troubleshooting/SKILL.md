---
name: powerbi-pbir-troubleshooting
description: Operational traps, UTF-8 BOM encoding fixes, slicer orientation values, PBID rewrite behaviors, and Python JSON manipulation templates.
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

## 🔗 RELATED SKILLS & REPOSITORY FILES

- 🏠 **[powerbi-pbir-editor](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-editor/SKILL.md)** - Master Skill Hub
- 📊 **[powerbi-pbir-visuals-specs](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-visuals-specs/SKILL.md)** - Visual Types & JSON Schemas
- 🚀 **[launch.py](file:///C:/Users/Sebas/desktop-ssas-mcp/launch.py)** - Launcher script avoiding PYTHONPATH collision
- 🛠️ **[fix_tmdl_format.py](file:///C:/Users/Sebas/desktop-ssas-mcp/fix_tmdl_format.py)** - TMDL format string sanitizer
