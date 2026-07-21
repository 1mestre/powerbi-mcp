# 5 Core Principles of Deterministic PBIR Styling & Layout

Master reference document for deterministic PBIR visual styling and multi-page layout architecture.

---

## 🟢 Principle 1: Programmatic Binding of Custom Visuals (AppSource)

**Failure cause:** Third-party custom visuals (`publicCustomVisuals`) in PBIR ignore field projections if `queryState` only includes `"Values"`. Most expect a manifest-specific internal role key (e.g. `"content"` for HTML Content).

**Rule for Agents:** When generating `visual.json` for a custom visual, duplicate the field projection in `queryState` under both `"Values"` AND the manifest-specific role key (`"content"`).

```json
"queryState": {
  "Values": { "projections": [...] },
  "content": { "projections": [...] }
}
```

---

## 🟢 Principle 2: Canvas Background (page.json) vs Theme JSON

**Failure cause:** `visualStyles.page.background` inside a theme JSON file is ignored by the PBIR rendering engine for the main canvas.

**Rule for Agents:** To set canvas background color (e.g. to `#0F3040` for dark themes or `#FFFFFF` for light themes), edit `page.json` directly under `objects.background`:

```json
"background": [{
  "properties": {
    "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#0F3040'" } } } } },
    "transparency": { "expr": { "Literal": { "Value": "0D" } } }
  }
}]
```

*(Note: `page.json` background does NOT accept the `show` property. Including `show` triggers a schema error: "Se ha incluido una propiedad 'show' adicional").*

---

## 🟢 Principle 3: Strict Color Key Mapping by Visual Type

**Failure cause:** Using generic property names like `"color"` or `"labelColor"` on incorrect visual types causes Power BI Desktop to ignore the setting and fall back to unstyled default colors.

**Rule for Agents — Master Key Table:**

| Visual Type | Main Value | Labels/Callouts | Axis Labels | Subtitle/Category |
|-------------|------------|-----------------|-------------|-------------------|
| **card (KPI)** | `"labels"` → `"color"` | — | — | `"categoryLabels"` → `"show": false` |
| **donutChart** | — | `"labels"` → `"color"` | — | Legend: `"legend"` → `"labelColor"` |
| **barChart/columnChart** | `"dataPoint"` → `"fill"` | `"dataLabels"` → `"labelColor"` | `"categoryAxis"`/`"valueAxis"` → `"labelColor"` | Axis titles: `"titleColor"` or `"showTitle": false` |
| **slicer** | — | `"items"` → `"fontColor"` | — | `"header"` → `"show": false` |

---

## 🟢 Principle 4: Force Multi-Color Bars (`scopeId` Selectors)

**Failure cause:** Assigning a single object to `objects.dataPoint` renders all category bars monochrome.

**Rule for Agents:** To force distinct colors per category bar, inject an array of `scopeId` Comparison selectors into `objects.dataPoint`. `Comparison.Right` MUST contain `Literal` directly without an outer `expr` wrapper:

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

---

## 🟢 Principle 5: Grid 1280x720 & Safety Margins (Anti-Crowding)

**Failure cause:** Continuous x/y coordinates without margins cause visual overlap or canvas boundary overflow.

**Rule for Agents:**
- **Canvas Reference:** Standard `1280 x 720` (or `1280 x 920`).
- **Canvas Margins:** Minimum `20px` to canvas edges (`x_min=20`, `x_max=1260`, `y_min=20`, `y_max=700`).
- **Inter-Visual Spacing (Gaps):** Minimum `20px` between adjacent visual containers.
- **Page Capacity Limits:** Max **5-6 visuals per page** (KPIs/Slicers `h >= 100px`; Charts `h >= 260px`).
- **KPI Row Grid Math (5 KPIs max per row):** Card width `232px`, `gap=20px`, `margin=20px`. Formula: `x_i = 20 + i * 252` for `i = 0..4`.

---

## 🔑 Schema Version Lock (MUST MATCH)

**CRITICAL**: Every `visual.json` `$schema` MUST match the `visual` version declared in `report.json`:
- If `report.json` has `"visual": "2.9.0"` → ALL `visual.json` must use schema `.../visualContainer/2.9.0/schema.json`
- Mismatch (e.g., 2.10.0 vs 2.9.0) → Power BI Desktop silently ignores the visual, rendering defaults.

---

## 📦 `visualContainerObjects` vs `objects` — Strict Separation

| Section | Valid Keys | Forbidden |
|---------|------------|-----------|
| **visualContainerObjects** | `title`, `subTitle`, `background`, `border`, `visualTooltip`, `dropShadow`, `visualHeader`, `stylePreset` | `legend`, `categoryAxis`, `valueAxis`, `dataPoint`, `dataLabels`, `labels`, `header`, `items`, `inputText`, `cardLabels` |
| **objects** | `categoryAxis`, `valueAxis`, `legend`, `labels`, `dataLabels`, `dataPoint`, `cardLabels`, `categoryLabels`, `header`, `items`, `inputText`, `general` (slicer) | `title`, `background`, `border`, `subTitle`, `visualTooltip`, `dropShadow` |

---

## 📋 Pre-Flight Checklist

- [ ] `report.json` → verify `"visual": "2.9.0"` → set `$schema` in ALL `visual.json` files
- [ ] `page.json` → `background.color = '#0F3040'` (without `show` property)
- [ ] KPIs: `visualContainerObjects` with background/border, `objects` = `labels` + `categoryLabels`
- [ ] Slicer: `objects.header.show:false`, `objects.items.fontColor/fontSize`, NO `orientation` in `general`
- [ ] Donut: `objects.labels.color=white`, `objects.legend.labelColor=light gray`
- [ ] Bar charts: `objects.dataPoint` with `scopeId` selectors array for multi-color
- [ ] Custom visual: `queryState` with `Values` + `content` dual projection
- [ ] Run `python scripts/apply_theme.py "<Project>.pbip" --theme slate-terracotta`
- [ ] Run `python scripts/check_overlaps.py "<Project>.pbip"` -> expect 0 errors
- [ ] Delete `cache.abf` before opening Power BI Desktop
