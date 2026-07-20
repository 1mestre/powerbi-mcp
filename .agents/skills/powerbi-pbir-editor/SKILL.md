---
name: powerbi-pbir-editor
description: Master hub and workflow rules for programmatically editing Power BI Projects (PBIR format), TMDL measure files, and generating HTML visual measures via the generate_html_visual MCP tool.
---

# Power BI PBIR & TMDL Developer Skill (Master Hub)

Use this skill as the main entry point and workflow coordinator when you need to programmatically add or modify visuals in a Power BI Project (PBIP/PBIR format) or append DAX measures to Tabular Model Definition Language (TMDL) files.

---

## ⚠️ GOLDEN RULES TO AVOID EMPTY VISUALS IN PBIR 2.0.0+

1. **Folder Structure:** Visuals must be saved in individual folders under the `visuals/` subfolder. Example: `pages/{page-guid}/visuals/{visual-guid}/visual.json`. Do not save them loose in the page folder.
2. **REQUIRED `name` Property at Root (CRITICAL):** Each `visual.json` MUST include a `name` property at root level matching its folder name (e.g., `"vis_00"`), 1-50 chars. Without it Power BI throws: *"La propiedad necesaria 'name' no se incluyó en la propiedad root"*.
3. **Correct JSON Format:** Do not put `projections`, `filters`, or `query` on the root of `visual.json` or directly under `visual`. Projections must reside strictly inside `visual.query.queryState`:
   ```json
   "visual": {
     "visualType": "treemap",
     "query": {
       "queryState": {
         "Group": { "projections": [ ... ] },
         "Values": { "projections": [ ... ] }
       }
     },
     "drillFilterOtherVisuals": true,
     "objects": {},
     "visualContainerObjects": {}
   }
   ```
4. **Column vs Measure (CRITICAL):** Grouped charts (such as `treemap`, `funnel`, `barChart`, `columnChart`, `pieChart`, `donutChart`, `lineChart`, etc.) **DO NOT accept direct columns (`"Column"`) in their values projection (`Y` or `Values`)**. If you attempt to use a column directly in the Y-axis/Values axis, the visual will render as an **empty rectangle** in Power BI Desktop showing the "Select or drag fields" warning.
   - **Solution:** You must first create a DAX measure (`measure`) in the corresponding `.tmdl` file (using the `add_measure_to_tmdl` tool or modifying it directly), for example: `measure 'Average Service' = AVERAGE(table[service])`.
   - **Reference:** In the visual JSON, point to that measure using the `"Measure"` projection type (not `"Column"`):
     ```json
     "Y": {
       "projections": [
         {
           "field": {
             "Measure": {
               "Expression": { "SourceRef": { "Entity": "comidasrapidas" } },
               "Property": "Average Service"
             }
           },
           "queryRef": "comidasrapidas.Average Service",
           "nativeQueryRef": "Average Service"
         }
       ]
     }
     ```
   - Direct `"Column"` projections are only allowed in table visuals (`tableEx`) or in the grouping fields (like `Category`, `Group`, or `Legend`) of charts.

---

## 🛠️ CRITICAL ENVIRONMENT & WORKFLOW RULES

* **Close Power BI Before Edits (CRITICAL WORKFLOW):** You **MUST** run `taskkill /IM PBIDesktop.exe /F` **BEFORE** making any changes to `.Report` or `.SemanticModel` files (TMDL/PBIR). If Power BI Desktop is open, it holds the files in memory and will completely overwrite the directory on save or close, wiping out your generated pages and visuals.
* **Clear Schema Cache (CRITICAL):** When performing a major schema refactoring, you **MUST** delete the `.SemanticModel/.pbi/cache.abf` file while Power BI Desktop is closed. This prevents conflicting cached schema evaluation loops.
* **Root Git Repositories:** Ensure no `.git` folder exists in `C:\` or `D:\` roots. This causes Power BI's automatic Git integration to try to write a `.gitignore` to the root drive, triggering an access permission crash.
* **Recommended Visual Creation Workflow:**
  1. Close PBID (`taskkill /IM PBIDesktop.exe /F`).
  2. Use `pbir add visual <type> "$page" -n "name" -t "Title" -x X -y Y -w W -h H -d "Role:table.field"` to create base structure.
  3. Add `objects` and styling via Python script (see [powerbi-pbir-troubleshooting](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-troubleshooting/SKILL.md)).
  4. Reopen PBID.

---

## 🔗 MODULAR SKILL DIRECTORY (INTERCONNECTED SKILLS)

This master skill is connected with four specialized sub-skills for fast and focused reference:

1. 📊 **[powerbi-pbir-visuals-specs](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-visuals-specs/SKILL.md)**
   - Built-in `visualType` identifiers, projection bindings by chart type (`tableEx`, `card`, `donutChart`, `barChart`, `lineChart`), and strict separation of `objects` vs `visualContainerObjects`.

2. 📐 **[powerbi-tmdl-modeling](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-tmdl-modeling/SKILL.md)**
   - TMDL file rules (single-line `//` comments), double-quoted `formatString`, measure creation, `discourageImplicitMeasures`, avoiding `%` in measure names, and preserving partition blocks.

3. 🎨 **[powerbi-design-layout-themes](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-design-layout-themes/SKILL.md)**
   - 1280x920 grid metrics, layout safety margins, KPI zero-crop rules, WCAG 2.1 AA contrast formulas, `ThemeDataColor` mapping indices, and 5 Premium Themes catalogue.

4. 🔧 **[powerbi-pbir-troubleshooting](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-troubleshooting/SKILL.md)**
   - Operational traps, UTF-8 without BOM encoding fixes, slicer `orientation` values (`0`, `1`, `2`), PBID rewrite behavior, treemap `dataPoint` rules, root property errors, and Python JSON script templates.

---

## 💻 MCP TOOLS — FULL REFERENCE (5 TOOLS)

All tools are registered in **[server.py](file:///C:/Users/Sebas/desktop-ssas-mcp/server.py)** and available via the `powerbi-local` MCP server.

| Tool | Purpose |
|---|---|
| `list_instances()` | Scan local AppData and return all active Power BI Desktop SSAS ports |
| `get_schema(port)` | Return full semantic model schema: tables, columns, types, visibility |
| `execute_dax(port, query)` | Run any DAX EVALUATE query; returns JSON-safe list of row dicts |
| `add_measure_to_tmdl(tmdl_path, name, expression, format_string?)` | Write a DAX measure permanently to a `.tmdl` file |
| `generate_html_visual(port, query, chart_type, label_key, value_key, ...)` | **NEW** — Execute DAX + generate HTML visual + optionally write to TMDL |

### `generate_html_visual` — Quick Reference

Inspired by [Power-BI-Visuals-Using-Claude-AI-HTML-DAX (Fasaclox)](https://github.com/Fasaclox/Power-BI-Visuals-Using-Claude-AI-HTML-DAX). Generates self-contained HTML strings for Power BI's **HTML Content** visual.

**Supported `chart_type` values:** `"bar"`, `"donut"`, `"kpi"`, `"clustered_bar"`, `"stacked_column"`, `"line"`, `"table"`

**Key parameters:**
- `port` — from `list_instances()`
- `query` — DAX EVALUATE string
- `label_key` / `value_key` — column names from the query result
- `series_json` — JSON array for multi-series: `'[{"key":"col","label":"Name","color":"#hex"}]'`
- `tmdl_path` + `measure_name` — if both provided, writes the HTML as a DAX measure to the `.tmdl` file

**Returns:** `{"html": "<style>...</style><div>...", "chart_type": "bar", "row_count": 12, "tmdl_result": "..."}`

**To display in Power BI:** Add the **HTML Content** visual (Daniel Marsh-Patrick, AppSource) to the page. Bind the DAX measure that returns the HTML string to the visual's Values field.

### HTML Visual Types — Available in `html_generators.py`

See **[html_generators.py](file:///C:/Users/Sebas/desktop-ssas-mcp/html_generators.py)** for full implementation:

| Function | Visual |
|---|---|
| `gen_bar_chart(data, label_key, value_key, title, color, ...)` | Horizontal gauge bar chart |
| `gen_donut_chart(data, label_key, value_key, title, colors)` | SVG donut ring chart with legend |
| `gen_kpi_card(value, target, label, ...)` | KPI attainment card with progress bar |
| `gen_clustered_bar(data, label_key, series, title)` | Multi-series clustered horizontal bars |
| `gen_stacked_column(data, label_key, series, title)` | Vertical stacked column chart (SVG) |
| `gen_line_chart(data, x_key, series, title)` | SVG polyline time-series chart |
| `gen_html_table(data, columns, title, stripe)` | Styled HTML table with zebra striping |

### Other Repository Files

* 🔌 **[pbi_connector.py](file:///C:/Users/Sebas/desktop-ssas-mcp/pbi_connector.py)** - ADOMD.NET connector: port scanner + DAX execution engine
* 📈 **[create_dashboard.py](file:///C:/Users/Sebas/desktop-ssas-mcp/create_dashboard.py)** - Standalone Plotly browser dashboard from live DAX data
* 🛠️ **[fix_tmdl_format.py](file:///C:/Users/Sebas/desktop-ssas-mcp/fix_tmdl_format.py)** - Sanitize unquoted `formatString` entries in `.tmdl` files
* 🚀 **[launch.py](file:///C:/Users/Sebas/desktop-ssas-mcp/launch.py)** - Sanitizing launcher: clears `PYTHONPATH`/`PYTHONHOME` before boot
* 📖 **[README.md](file:///C:/Users/Sebas/desktop-ssas-mcp/README.md)** - Full setup, tool reference, and agent installation prompt
