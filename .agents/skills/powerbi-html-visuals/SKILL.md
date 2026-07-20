---
name: powerbi-html-visuals
description: Rules, patterns, and tool usage for generating HTML visual measures using the generate_html_visual MCP tool and html_generators.py. Use this skill when creating bar charts, donut charts, KPI cards, or any HTML-based visual inside Power BI using the HTML Content visual and DAX+HTML pattern.
---

# Power BI HTML Visual Generator Skill

Use this skill when you need to generate custom HTML-rendered charts or KPI cards inside Power BI using the **HTML Content** visual (by Daniel Marsh-Patrick). This replaces the need for AppSource custom chart visuals for many common use cases.

This skill integrates the pattern from [Power-BI-Visuals-Using-Claude-AI-HTML-DAX (Fasaclox)](https://github.com/Fasaclox/Power-BI-Visuals-Using-Claude-AI-HTML-DAX) into the MCP server workflow via the `generate_html_visual` tool and `html_generators.py`.

---

## ⚙️ How the DAX+HTML Pattern Works

1. A DAX measure returns a **plain HTML string** (a scalar `TEXT` value).
2. The **HTML Content** visual (AppSource, by Daniel Marsh-Patrick) receives that string and renders it inside a sandboxed `<iframe>`.
3. The iframe is isolated — **no external scripts, no CDN, no cookies**. Everything must be inline HTML + CSS + SVG.
4. Power BI applies no transformations to the string — what the measure returns is exactly what renders.

**Minimal example DAX measure:**
```dax
My Chart = "<div style='font-family:Segoe UI;padding:10px;font-size:14px;color:#1e293b'>Hello HTML</div>"
```

---

## 🛠️ generate_html_visual — MCP Tool

The `generate_html_visual` tool in [server.py](file:///C:/Users/Sebas/desktop-ssas-mcp/server.py) automates the full pipeline:

```
execute DAX query → sanitize data → generate HTML → (optionally write to .tmdl)
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `port` | str | ✅ | SSAS port from `list_instances()` |
| `query` | str | ✅ | DAX EVALUATE query |
| `chart_type` | str | ✅ | See chart types table below |
| `label_key` | str | ✅ | Column name for labels / X-axis |
| `value_key` | str | ✅ | Column name for primary values |
| `title` | str | — | Chart title |
| `series_json` | str | — | JSON array for multi-series: `'[{"key":"col","label":"Name","color":"#hex"}]'` |
| `value_prefix` | str | — | Prefix for values (e.g. `"$"`) |
| `value_suffix` | str | — | Suffix for values (e.g. `" units"`) |
| `value_decimals` | int | — | Decimal places (default: `0`) |
| `color` | str | — | Primary colour for single-series charts (hex, default: `"#3b82f6"`) |
| `tmdl_path` | str | — | Absolute path to `.tmdl` file — if set with `measure_name`, writes the measure |
| `measure_name` | str | — | Name for the DAX measure written to TMDL |

### Supported Chart Types

| `chart_type` | Description | Required extra params |
|---|---|---|
| `"bar"` | Horizontal gauge-style bar chart | — |
| `"donut"` | SVG donut ring chart with legend | — |
| `"kpi"` | KPI attainment card with progress bar | `series_json: [{"key":"<target_col>"}]` |
| `"clustered_bar"` | Multi-series clustered horizontal bars | `series_json` with multiple series |
| `"stacked_column"` | Vertical stacked column chart (SVG) | `series_json` with multiple series |
| `"line"` | SVG polyline time-series chart | `series_json` for multiple series |
| `"table"` | Styled HTML table with zebra striping | `series_json` for column config |

### Return Value

```json
{
  "html": "<style>...</style><div>...</div>",
  "chart_type": "bar",
  "row_count": 12,
  "tmdl_result": "Successfully added measure 'HTML Sales by Country' to Sales.tmdl"
}
```

---

## 📋 Step-by-Step Agent Workflow

### 1. Single-Series Bar Chart (simplest)

```
1. list_instances()
   → port = "54321"

2. get_schema("54321")
   → find table "Sales", columns "Country", "NetSales"

3. generate_html_visual(
     port="54321",
     query='EVALUATE SUMMARIZECOLUMNS(
              "Sales"[Country],
              "Total", SUM("Sales"[NetSales])
            )',
     chart_type="bar",
     label_key="Country",
     value_key="Total",
     title="Net Sales by Country",
     value_prefix="$",
     value_decimals=0,
     color="#10b981",
     tmdl_path="C:/path/Sales.SemanticModel/definition/tables/Sales.tmdl",
     measure_name="HTML Sales by Country"
   )
   → HTML generated + measure written to .tmdl

4. In the report .pbip:
   - Add the HTML Content visual to the page's visual.json
   - Bind measure "HTML Sales by Country" to the Values field
```

### 2. Multi-Series Clustered Bar

```
generate_html_visual(
  port="54321",
  query='EVALUATE SUMMARIZECOLUMNS(
           "Sales"[Region],
           "Sales", SUM("Sales"[Amount]),
           "Cost",  SUM("Sales"[Cost])
         )',
  chart_type="clustered_bar",
  label_key="Region",
  value_key="Sales",
  title="Sales vs Cost by Region",
  series_json='[
    {"key":"Sales","label":"Net Sales","color":"#3b82f6"},
    {"key":"Cost","label":"Cost",      "color":"#ef4444"}
  ]'
)
```

### 3. KPI Attainment Card

```
generate_html_visual(
  port="54321",
  query='EVALUATE ROW(
           "Revenue",  [Total Revenue],
           "Target",   [Revenue Target]
         )',
  chart_type="kpi",
  label_key="",
  value_key="Revenue",
  title="Revenue Attainment",
  series_json='[{"key":"Target"}]',
  value_prefix="$",
  value_decimals=2
)
```

---

## 🎨 HTML Visual Design Conventions

All visuals generated by `html_generators.py` follow this design system:

| Property | Value |
|---|---|
| Font | `Segoe UI, sans-serif` (native Power BI font) |
| CSS scope | Short unique class names — no conflicts inside iframe |
| External resources | **None** — no CDN, no external fonts, no JS libraries |
| Rendering engine | Inline HTML + CSS + SVG only |
| Color palette | Tailwind-inspired: `#3b82f6` blue, `#10b981` green, `#ef4444` red, `#f59e0b` amber |
| Responsive | Flex layouts adapt to visual container width |

---

## ⚠️ Critical Rules for HTML Measures in TMDL

1. **Escape internal double-quotes:** Any `"` inside the HTML must be doubled: `"` → `""` in DAX string literals.
   ```dax
   measure 'Chart' = "<div style=""color:#1e293b"">Hello</div>"
   ```
2. **No `formatString`:** HTML measures return text — never add a `formatString` to them.
3. **No `RETURN` table syntax:** The measure must be a scalar expression, not a table.
4. **No `EVALUATE`:** `EVALUATE` is for DAX queries (execute_dax), not for measure expressions.
5. **Duplicate check:** Always scan the `.tmdl` file for an existing measure with the same name before writing.
6. **Partition block:** Never touch the `partition` block at the bottom of the `.tmdl` file.

---

## 🔗 Related Files & Skills

- ⚡ **[server.py](file:///C:/Users/Sebas/desktop-ssas-mcp/server.py)** — `generate_html_visual` tool implementation
- 📊 **[html_generators.py](file:///C:/Users/Sebas/desktop-ssas-mcp/html_generators.py)** — 7 HTML visual generator functions
- 📐 **[powerbi-tmdl-modeling](file:///C:/Users/Sebas/.gemini/config/skills/powerbi-tmdl-modeling/SKILL.md)** — TMDL measure syntax and indentation rules
- 🏠 **[powerbi-pbir-editor](file:///C:/Users/Sebas/.gemini/config/skills/powerbi-pbir-editor/SKILL.md)** — Master skill hub (PBIR + visual.json)
- 📖 **[README.md](file:///C:/Users/Sebas/desktop-ssas-mcp/README.md)** — Full setup and tool reference
