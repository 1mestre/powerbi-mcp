---
name: powerbi-pbir-editor
description: Guidelines and schemas for programmatically creating Power BI visuals in PBIR JSON format and editing TMDL measure files.
---

# Power BI PBIR & TMDL Developer Skill

Use this skill when you need to programmatically add or modify visuals in a Power BI Project (PBIP/PBIR format) or append DAX measures to Tabular Model Definition Language (TMDL) files.

---

## ⚠️ REGLAS DE ORO PARA EVITAR GRÁFICOS VACÍOS EN PBIR 2.0.0+

1. **Estructura de Carpetas:** Los visuales deben guardarse en carpetas individuales bajo la subcarpeta `visuals/`. Ejemplo: `pages/{page-guid}/visuals/{visual-guid}/visual.json`. No sueltos en la carpeta de la página.
2. **Formato JSON Correcto:** No pongas `projections`, `filters` o `query` en la raíz de `visual.json` ni directamente bajo `visual`. Las proyecciones deben ir obligatoriamente en `visual.query.queryState`:
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
3. **Column vs Measure (CRÍTICO):** Los gráficos agrupados (como `treemap`, `funnel`, `barChart`, `columnChart`, `pieChart`, `donutChart`, etc.) **NO aceptan columnas directas (`"Column"`) en su proyección de valores (`Y` o `Values`)**. Si intentas usar una columna directamente en el eje Y, el gráfico se renderizará como un **rectángulo vacío** en Power BI Desktop.
   - **Solución:** Primero debes crear una medida DAX (`measure`) en el archivo `.tmdl` correspondiente (usando la herramienta `add_measure_to_tmdl`), por ejemplo: `measure 'Promedio Servicio' = AVERAGE(tabla[servicio])`.
   - **Referencia:** En el JSON del visual, debes apuntar a esa medida usando la proyección de tipo `"Measure"` (no `"Column"`):
     ```json
     "Y": {
       "projections": [
         {
           "field": {
             "Measure": {
               "Expression": { "SourceRef": { "Entity": "comidasrapidas" } },
               "Property": "Promedio Servicio"
             }
           },
           "queryRef": "comidasrapidas.Promedio Servicio",
           "nativeQueryRef": "Promedio Servicio"
         }
       ]
     }
     ```
   - Las proyecciones de tipo `"Column"` directo sólo se permiten en tablas (`tableEx`) o en el campo `Category`/`Group` de los gráficos.

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
Map fields inside `visuals/{visual-name}/visual.json` under `visual.query.queryState` using the format described in the Golden Rules above.

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

## 5. TMDL Measure & Partition Rules
When appending or modifying measures in a local `.tmdl` file:
* **Duplicate Prevention:** Check if the measure name already exists in the file to avoid compiling duplicates.
* **Double-Quoting Format Strings:** If `formatString` contains spaces, currencies, or symbols, **always** enclose it in double quotes:
  - `formatString: "$#,##0"` (Correct)
  - `formatString: $#,##0` (Incorrect - will crash Power BI on open)
* **Partition Preservation (CRÍTICO):** **NEVER** modify or delete the `partition {tabla} = m` block or the `annotation PBI_ResultType = Table` block located at the bottom of the `.tmdl` file. Deleting the partition block will cause a fatal load crash in Power BI Desktop with the error: `"Todas las tablas deben contener al menos una partición con la propiedad Full DataView"`. Any automated regex or parsing scripts to wipe/add measures must leave the partition block untouched.

---

## 6. Environment & Storage Warnings
* **Root Git Repositories:** Ensure no `.git` folder exists in `C:\` or `D:\` roots. This causes Power BI's automatic Git integration to try to write a `.gitignore` to the root drive, triggering an access permission crash.
* **Close Power BI Before Edits:** Always kill Power BI Desktop (`taskkill /IM PBIDesktop.exe /F`) before editing PBIR JSON or TMDL files, as it caches files in memory and will overwrite your changes on save or close.
