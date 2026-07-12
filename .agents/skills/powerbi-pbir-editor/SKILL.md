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

## 2. Directory Structure for Visuals (PBIR 2.0.0+ / page 2.x.x)
In modern PBIR reports, visual files **must not** be placed directly in the page folder. They must be organized inside a `visuals/` subfolder, where each visual is its own directory containing a `visual.json` file:
```
{proyecto}.Report/
  definition/
    pages/
      {page-guid}/
        page.json
        visuals/
          {visual-name}/
            visual.json
```

---

## 3. Projection Bindings by Chart Type (visualContainer Schema)
Map fields inside `visuals/{visual-name}/visual.json` under `visual.query.queryState` using the following exact format and channel keys:

* **Category**: X-axis/y-axis dimension.
* **Y**: Metric value/measure.
* **Values**: For flat tables (`tableEx`) or multi-row cards.

### ⚠️ Aggregation Rule (CRITICAL)
In the modern `visualContainer` schema:
1. Chart visuals (treemap, funnel, barChart, columnChart, etc.) **cannot** aggregate columns directly in the visual JSON. If you put a `"Column"` projection on the Y-axis/Values of a chart, it will render as an **empty rectangle**.
2. **You must first define a DAX measure in the table's TMDL file** (e.g. `measure 'Total Sales' = SUM('Sales'[Amount])` or `measure 'Promedio Edad' = AVERAGE('comidasrapidas'[edad])`).
3. Reference that measure in `visual.json` using the `"Measure"` projection type:

```json
"Category": {
  "projections": [
    {
      "field": {
        "Column": {
          "Expression": { "SourceRef": { "Entity": "comidasrapidas" } },
          "Property": "genero"
        }
      },
      "queryRef": "comidasrapidas.genero",
      "nativeQueryRef": "genero"
    }
  ]
},
"Y": {
  "projections": [
    {
      "field": {
        "Measure": {
          "Expression": { "SourceRef": { "Entity": "comidasrapidas" } },
          "Property": "Promedio Edad"
        }
      },
      "queryRef": "comidasrapidas.Promedio Edad",
      "nativeQueryRef": "Promedio Edad"
    }
  ]
}
```

### Table Visuals (tableEx)
Flat tables (`tableEx`) can use direct `"Column"` references without aggregations inside `"Values"`:
```json
"queryState": {
  "Values": {
    "projections": [
      {
        "field": {
          "Column": {
            "Expression": { "SourceRef": { "Entity": "comidasrapidas" } },
            "Property": "nse"
          }
        },
        "queryRef": "comidasrapidas.nse",
        "nativeQueryRef": "nse"
      }
    ]
  }
}
```

---

## 4. Formatting and Titles in visual.json
To set visual titles programmatically in `visualContainer` format:
```json
"visualContainerObjects": {
  "title": [
    {
      "properties": {
        "show": {
          "expr": { "Literal": { "Value": "true" } }
        },
        "text": {
          "expr": { "Literal": { "Value": "'My Visual Title'" } }
        }
      }
    }
  ]
}
```

---

## 5. TMDL Measure Rules
When appending measures to a local `.tmdl` file:
* **Duplicate Prevention:** Check if the measure name already exists in the file to avoid compiling duplicates.
* **Double-Quoting Format Strings:** If `formatString` contains spaces, currencies, or symbols, **always** enclose it in double quotes:
  - `formatString: "$#,##0"` (Correct)
  - `formatString: $#,##0` (Incorrect - will crash Power BI on open)

---

## 6. Environment & Storage Warnings
* **Root Git Repositories:** Ensure no `.git` folder exists in `C:\` or `D:\` roots. This causes Power BI's automatic Git integration to try to write a `.gitignore` to the root drive, triggering an access permission crash.
* **Close Power BI Before Edits:** Always kill Power BI Desktop (`taskkill /IM PBIDesktop.exe /F`) before editing PBIR JSON or TMDL files, as it caches files in memory and will overwrite your changes on save or close.
