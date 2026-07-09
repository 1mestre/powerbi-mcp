---
name: powerbi-pbir-editor
description: Guidelines and schemas for programmatically creating Power BI visuals in PBIR JSON format and editing TMDL measure files.
---

# Power BI PBIR & TMDL Developer Skill

Use this skill when you need to programmatically add or modify visuals in a Power BI Project (PBIP/PBIR format) or append DAX measures to Tabular Model Definition Language (TMDL) files.

---

## 1. Valid PBIR visualType Identifiers
Never use legacy, descriptive, or regional names (e.g., `columnStackedChart` or `clusteredBarChart`). Only use the official Power BI built-in identifiers:

* **Comparisons & Trends:**
  - `"columnChart"` (handles both clustered column and stacked column layouts)
  - `"barChart"` (handles both clustered bar and stacked bar layouts)
  - `"lineChart"` (line chart)
  - `"areaChart"` (area chart)
  - `"ribbonChart"` (ribbon chart for rank transitions)
  - `"lineClusteredColumnComboChart"` (combo column + line chart)
* **Compositions:**
  - `"pieChart"` (pie chart)
  - `"donutChart"` (donut chart)
  - `"treemap"` (treemap)
  - `"funnel"` (embudo / funnel chart)
* **Summaries & Tables:**
  - `"table"` (flat data table)
  - `"matrix"` (matrix / pivot table)
* **KPIs & Metrics:**
  - `"card"` (single value KPI card)
  - `"multiRowCard"` (multi-row card visual)
  - `"gauge"` (radial gauge / medidor)
* **Advanced:**
  - `"scatterChart"` (scatter / bubble plot)
  - `"slicer"` (slicer controls)

---

## 2. Projection Bindings by Chart Type
Map fields inside `visual.json` under `queryState` using the following exact channel keys:

### columnChart, barChart, lineChart, areaChart, ribbonChart
* **`Category`**: The x-axis/y-axis dimension (e.g., `Month`, `Brand`).
* **`Y`**: The measure values (e.g., `Ventas Netas USD`).
* **`Series`**: (Optional) Legend field to cluster/stack the chart.

### pieChart, donutChart, funnel
* **`Category`**: Slice/Category dimension (e.g., `Species`, `Region`).
* **`Y`**: Metric/Value (e.g., `Ventas Netas USD`).

### treemap
* **`Group`**: Top-level category (e.g., `Country`).
* **`Details`**: (Optional) Inner sub-category (e.g., `Brand`).
* **`Values`**: Metric/Value.

### scatterChart
* **`Category`**: Bubble identifiers (e.g., `Brand`).
* **`X`**: X-Axis numerical measure.
* **`Y`**: Y-Axis numerical measure.
* **`Size`**: (Optional) Bubble size measure (e.g., `Unidades Totales`).

### table & multiRowCard
* **`Values`**: Flat array of column and measure projections.

### matrix
* **`Rows`**: Dimensions for rows (e.g., `Brand`).
* **`Columns`**: (Optional) Dimensions for columns.
* **`Values`**: Measures for cell values.

### card & gauge
* **`Y`**: The main KPI value projection.

---

## 3. Formatting and Titles in visual.json
To set visual titles programmatically in PBIR format:
```json
"visualContainerObjects": {
  "title": [{
    "properties": {
      "text": {"expr": {"Literal": {"Value": "'My Visual Title'"}}},
      "fontSize": {"expr": {"Literal": {"Value": "14D"}}}
    }
  }]
}
```

---

## 4. TMDL Measure Rules
When appending measures to a local `.tmdl` file:
* **Duplicate Prevention:** Check if the measure name already exists in the file to avoid compiling duplicates.
* **Double-Quoting Format Strings:** If `formatString` contains spaces, currencies, or symbols, **always** enclose it in double quotes:
  - `formatString: "$#,##0"` (Correct)
  - `formatString: $#,##0` (Incorrect - will crash Power BI on load)

---

## 5. Environment & Storage Warnings
* **Root Git Repositories:** Ensure no `.git` folder exists in `C:\` or `D:\` roots. This causes Power BI's automatic Git integration to try to write a `.gitignore` to the root drive, triggering an access permission crash.
* **Cache Management:** Deleting `.pbi/cache.abf` is a useful troubleshooting step to force a clean metadata rebuild, but always advise the user to click **`Actualizar`** (Refresh) and save (Ctrl + S) immediately after opening to recreate the cache and remove yellow warning banners.
