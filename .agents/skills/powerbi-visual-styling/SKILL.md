---
name: powerbi-visual-styling
description: >-
  Visual styling rules for PBIP dashboards — dark/light theme contrast, 
  per-visual-type text colors, bar chart color rules, schema validation,
  CSV data pipeline, and encoding fixes. Works alongside powerbi-orchestrator.
tags: [powerbi, styling, theme, contrast, dark-mode, visual, pbip]
---

# Power BI Visual Styling Rules

**⚠️ LOAD ALONGSIDE `powerbi-orchestrator`.** This skill provides the styling rules
that the orchestrator's Phase 6 (Theme & Styling) needs but doesn't encode.

---

## 🚨 CRITICAL RULES

## 🚨 CRITICAL RULES

| # | Rule | Why |
|---|------|-----|
| 1 | **ALWAYS set text colors explicitly per visual.json** | Theme cascading is unreliable; PBID ignores theme per-element colors in many cases |
| 2 | **NEVER put legend/categoryAxis/dataPoint in visualContainerObjects** | Schema validation error → PBID rejects ALL styling for that visual |
|| 3 | **For categorical bar charts: dataPoint[] WITH scopeId selectors REQUIRED** | Single dataPoint = monochrome; must inject scopeId Comparison array per category (Pilar 4) |
|| 3b | **For temporal bar charts: NO dataPoint[]** | Single color correct for time-series data |
| 5 | **CSV must go through audit → fix pipeline first** | Unbalanced quotes + QuoteStyle.None = corrupt column data |
| 6 | **ALWAYS post-process visual.json after pbir** | pbir CLI has UTF-8 encoding bug in titles |
| 7 | **Theme must include firstLevelElements + secondLevelElements** | Without these, text defaults to #252423 (invisible on dark backgrounds) |
| 8 | **Schema version MUST match report.json visual version** | Mismatch (e.g. 2.10.0 vs 2.9.0) → PBID silently ignores visual, renders defaults |
| 9 | **visualContainerObjects background/border belong there, NOT in objects** | For KPI cards, background/border/radius in visualContainerObjects; objects only labels/categoryLabels |
| 10 | **Slicer: orientation in items, NOT general + responsive=false + h≥85px** | orientation="1" (horizontal tiles) MUST go in `items.orientation` with `general.responsive: false` + height≥85px; use orientation="2" (dropdown) for h≤55px; `header.show:false` in `objects` |
| 11 | **HTML Content custom visual needs dual projection** | Must have both "Values" AND "content" in queryState for auto-binding |
| 12 | **Slicer: orientation goes in items, NOT general** | Adding orientation under general breaks slicer (blank, no checkboxes); use `items.orientation: "1"` for horizontal tiles with `general.responsive: false` |

## 🎯 5 Core Deterministic PBIR Styling Principles

These 5 core principles eliminate infinite correction loops when working with PBIP/PBIR:

### 🟢 Principle 1: Programmatic Binding of Custom Visuals (AppSource)
**Failure cause:** Third-party visuals (`publicCustomVisuals`) in PBIR ignore projection if `queryState` only includes `"Values"`. Most use a manifest-specific internal role (e.g. `"content"` for HTML Content).
**Rule for Agents:** When generating `visual.json` for a custom visual, duplicate the field projection in `queryState` under both `"Values"` and the manifest-specific role key (`"content"`).

### 🟢 Principle 2: Canvas Background (page.json) vs Theme JSON
**Failure cause:** `visualStyles.page.background` inside a theme JSON file is ignored by the PBIR rendering engine for the main canvas.
**Rule for Agents:** To change canvas background color, edit `page.json` directly under `objects.background`:
```json
"background": [{
  "properties": {
    "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#0F3040'" } } } } },
    "transparency": { "expr": { "Literal": { "Value": "0D" } } }
  }
}]
```
*(Note: `page.json` background does NOT accept the `show` property; including it triggers a schema error).*

### 🟢 Principle 3: Strict Color Key Mapping by Visual Type
**Failure cause:** Using generic names like `"color"` or `"labelColor"` on incorrect visual types causes Power BI to ignore the setting and fall back to default colors.
**Rule for Agents:**
| Visual Type | Correct `objects` Key | Typical Value |
|-------------|-----------------------|---------------|
| **KPI Card (`card`)** | Callout value is formatted in `"labels"` (`"color"`). Subtitle is hidden in `"categoryLabels"` (`"show": false`). | `"color": "#FFFFFF"`, `"fontSize": 24D` |
| **Donut / Pie Chart (`donutChart`)** | Callout labels set in `"labels"` using `"color"`. Legend set in `"legend"` using `"labelColor"`. | `"color": "#FFFFFF"` |
| **Bar / Column (`barChart` / `columnChart`)** | Axis label color is `"labelColor"`, title color is `"titleColor"` (or `"showTitle": false`). | `"labelColor": "#94A3B8"` |

### 🟢 Principle 4: Force Multi-Color Bars (`scopeId` Selectors)
**Failure cause:** Assigning a single object to `objects.dataPoint` renders all bars monochrome.
**Rule for Agents:** To force distinct colors per bar, inject an array of `scopeId` Comparison selectors into `objects.dataPoint`. `Comparison.Right` MUST contain `Literal` directly without an outer `expr` wrapper:
```json
"dataPoint": [
  {
    "properties": { "fill": { "solid": { "color": { "expr": { "Literal": { "Value": "'#E50914'" } } } } } },
    "selector": {
      "metadata": "Table.Column",
      "data": [{
        "scopeId": {
          "Comparison": {
            "ComparisonKind": 0,
            "Left": { "Column": { "Expression": { "SourceRef": { "Entity": "Table" } }, "Property": "Column" } },
            "Right": { "Literal": { "Value": "'CategoryValue'" } }
          }
        }
      }]
    }
  }
]
```

### 🟢 Principle 5: 1280x720 Grid & Safety Margins
**Failure cause:** Continuous x/y coordinates without gaps cause visual collapse or overlap.
**Rule for Agents:**
- **Canvas Reference:** Standard `1280 x 720` (or `1280 x 920`).
- **Canvas Margins:** Minimum `20px` to canvas edges (`x=20`, `y=20`).
- **Inter-Visual Spacing (Gaps):** Minimum `20px` between adjacent visual containers.
- **Page Capacity & Heights:** Max **5-6 visuals per page**. KPIs/Slicers `h >= 100px`; Charts `h >= 260px`. Max 5 KPIs per row (`w=232px`, `gap=20px`). Formula: `x_i = 20 + i * 252`.

---

## 🔑 Schema Version Lock (MUST MATCH)
**CRITICAL**: Every `visual.json` `$schema` MUST match the `visual` version declared in `report.json`:
- If `report.json` has `"visual": "2.9.0"` → ALL `visual.json` must use schema `.../visualContainer/2.9.0/schema.json`
- Mismatch (e.g., 2.10.0 vs 2.9.0) → PBID silently ignores the visual, renders defaults
- Always check `report.json` first, then set schema accordingly

### 📦 visualContainerObjects vs objects — Separación Estricta
- **visualContainerObjects**: `title`, `subTitle`, `background`, `border`, `visualTooltip`, `dropShadow` — CONTAINER only
- **objects**: `categoryAxis`, `valueAxis`, `legend`, `labels`, `dataLabels`, `dataPoint`, `cardLabels`, `categoryLabels`, `header`, `items`, `inputText`, `general` (slicer) — INTERNAL visual formatting
- **Card KPIs**: `background`/`border`/`radius` in `visualContainerObjects`; `objects` only `labels` + `categoryLabels`
- **Slicer**: `header.show:false` in `objects`; NO `orientation` in `general` (breaks slicer)
