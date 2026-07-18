---
name: powerbi-pbir-editor
description: Guidelines and schemas for programmatically creating Power BI visuals in PBIR JSON format and editing TMDL measure files.
---

# Power BI PBIR & TMDL Developer Skill

Use this skill when you need to programmatically add or modify visuals in a Power BI Project (PBIP/PBIR format) or append DAX measures to Tabular Model Definition Language (TMDL) files.

---

## ⚠️ GOLDEN RULES TO AVOID EMPTY VISUALS IN PBIR 2.0.0+

1. **Folder Structure:** Visuals must be saved in individual folders under the `visuals/` subfolder. Example: `pages/{page-guid}/visuals/{visual-guid}/visual.json`. Do not save them loose in the page folder.
2. **Correct JSON Format:** Do not put `projections`, `filters`, or `query` on the root of `visual.json` or directly under `visual`. Projections must reside strictly inside `visual.query.queryState`:
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
3. **Column vs Measure (CRITICAL):** Grouped charts (such as `treemap`, `funnel`, `barChart`, `columnChart`, `pieChart`, `donutChart`, `lineChart`, etc.) **DO NOT accept direct columns (`"Column"`) in their values projection (`Y` or `Values`)**. If you attempt to use a column directly in the Y-axis/Values axis, the visual will render as an **empty rectangle** in Power BI Desktop showing the "Select or drag fields" warning.
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
  - `"funnel"` (funnel chart)
* **Summaries & Tables:**
  - `"table"` (flat data table)
  - `"matrix"` (matrix / pivot table)
* **KPIs & Metrics:**
  - `"card"` (single value KPI card)
  - `"multiRowCard"` (multi-row card visual)
  - `"gauge"` (radial gauge)
* **Advanced:**
  - `"scatterChart"` (scatter / bubble plot)
  - `"slicer"` (slicer controls)

---

## 2. Directory Structure for Visuals (PBIR 2.0.0+ / page 2.x.x)
In modern PBIR reports, visual files **must not** be placed directly in the page folder. They must be organized inside a `visuals/` subfolder, where each visual is its own directory containing a `visual.json` file:
```
{project}.Report/
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

## 5. TMDL Model & Measure Rules
* **discourageImplicitMeasures Setting (CRITICAL):** If the model defines any Calculation Group (`calculationGroup`), you **MUST** set the property `discourageImplicitMeasures: true` under `model Model` in `model.tmdl`. Failure to do so will result in a load crash in Power BI Desktop.
* **Avoid isKey on Dimensions (CRITICAL):** Do not add `isKey: true` to primary key columns of standard import tables (like date or dimension tables). It can cause *"a cyclic reference was found during evaluation"* errors in Power Query. Use model-level relationships to map the keys.
* **Duplicate Prevention:** Check if the measure name already exists in the file to avoid compiling duplicates.
* **Double-Quoting Format Strings:** If `formatString` contains spaces, currencies, or symbols, **always** enclose it in double quotes:
  - `formatString: "$#,##0"` (Correct)
  - `formatString: $#,##0` (Incorrect - will crash Power BI on open)
* **Partition Preservation (CRITICAL):** **NEVER** modify or delete the `partition {table} = m` block or the `annotation PBI_ResultType = Table` block located at the bottom of the `.tmdl` file. Deleting the partition block will cause a fatal load crash in Power BI Desktop with the error: `"Todas las tablas deben contener al menos una partición con la propiedad Full DataView"`. Any automated regex or parsing scripts to wipe/add measures must leave the partition block untouched.

---

## 6. Environment, Schema & Workflow Rules (CRITICAL)
* **Root Git Repositories:** Ensure no `.git` folder exists in `C:\` or `D:\` roots. This causes Power BI's automatic Git integration to try to write a `.gitignore` to the root drive, triggering an access permission crash.
* **Close Power BI Before Edits (CRITICAL WORKFLOW):** You **MUST** run `taskkill /IM PBIDesktop.exe /F` **BEFORE** making any changes to `.Report` or `.SemanticModel` files (TMDL/PBIR). If Power BI Desktop is open, it holds the files in memory and will completely overwrite the directory on save or close, wiping out your generated pages and visuals.
* **Clear Schema Cache (CRITICAL):** When performing a major schema refactoring, you **MUST** delete the `.SemanticModel/.pbi/cache.abf` file while Power BI Desktop is closed. This prevents conflicting cached schema evaluation loops.
* **Valid JSON Keys (No "size", no "config" on root):** In modern `visualContainer` files, never write a `"size"`, `"config"`, or `"filters"` property on the root object of `visual.json`. Width and height must reside strictly inside `"position"`:
  ```json
  "position": {
    "x": 20,
    "y": 20,
    "z": 0,
    "width": 600,
    "height": 400,
    "tabOrder": 0
  }
  ```
* **Mandatory Projection Keys:** Every field projection inside the `"projections": [...]` array must contain `"queryRef"` and `"nativeQueryRef"` as string values. Failing to include these strings will cause a report load crash.
* **Page Folder Names:** Page folders under `pages/` must be named using 20-character lowercase hexadecimal strings or GUIDs. Do not use descriptive names.

---

## 7. Advanced Visual Customization & Styling (PBIR)
When styling visuals programmatically to ensure a custom, professional color palette:

### KPI Cards (Classic Card Visuals)
To style cards with solid backgrounds and white callout text:
- **Hide Category Label:** Target the `"categoryLabel"` object (not `"labels"`):
  ```json
  "categoryLabel": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "false" } } }
      }
    }
  ]
  ```
- **White Callout Value:** Target the `"labels"` object (not `"dataLabels"`):
  ```json
  "labels": [
    {
      "properties": {
        "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#FFFFFF'" } } } } },
        "fontSize": { "expr": { "Literal": { "Value": "24" } } }
      }
    }
  ]
  ```
- **White Title & Custom Background:** Set in `visualContainerObjects`:
  ```json
  "visualContainerObjects": {
    "background": [
      {
        "properties": {
          "show": { "expr": { "Literal": { "Value": "true" } } },
          "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#131921'" } } } } }
        }
      }
    ],
    "title": [
      {
        "properties": {
          "show": { "expr": { "Literal": { "Value": "true" } } },
          "text": { "expr": { "Literal": { "Value": "'Total Orders'" } } },
          "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#FFFFFF'" } } } } }
        }
      }
    ]
  }
  ```

### Donut Chart Slices Explicit Coloring
To override default theme colors for individual slices (e.g., coloring specific values like 'Amazon' or 'Merchant'), use `"dataPoint"` with a series selector using `scopeId` and a `Comparison` expression (never use raw `queryRef` or `value` under `data[0]`, which will throw schema validation errors):
```json
"objects": {
  "dataPoint": [
    {
      "properties": {
        "fill": { "solid": { "color": { "expr": { "Literal": { "Value": "'#131921'" } } } } }
      },
      "selector": {
        "metadata": "Fact_Sales.Fulfilment",
        "data": [
          {
            "scopeId": {
              "Comparison": {
                "ComparisonKind": 0,
                "Left": {
                  "Column": {
                    "Expression": { "SourceRef": { "Entity": "Fact_Sales" } },
                    "Property": "Fulfilment"
                  }
                },
                "Right": {
                  "Literal": { "Value": "'Amazon'" }
                }
              }
            }
          }
        ]
      }
    }
  ]
}
```

### Column & Line Chart Series Coloring
To set the color of columns or lines explicitly in a single-series visual (without legends):
- **Column Chart (using `"fill"`):**
  ```json
  "objects": {
    "dataPoint": [
      {
        "properties": {
          "fill": { "solid": { "color": { "expr": { "Literal": { "Value": "'#007185'" } } } } }
        }
      }
    ]
  }
  ```
- **Line Chart (using `"fillColor"`):** Always use `"fillColor"` rather than `"fill"` to customize standard line chart series colors explicitly in the JSON:
  ```json
  "objects": {
    "dataPoint": [
      {
        "properties": {
          "fillColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#FF9900'" } } } } }
        }
      }
    ]
  }
  ```

---

## 8. Canvas Grid & Layout Framework (Anti-Cramping & Visual Safety)
To prevent visuals from looking cramped, overlapping, or having low-contrast double labels:

### Layout Metrics & Spacing Grid:
- **Standard Canvas Dimensions:** Use `1280` (width) x `920` (height) to support vertical scrolling and provide ample breathing room.
- **Minimum Margins:** Maintain a `20px` margin on the left, right, top, and bottom edges of the canvas.
- **Minimum Inter-Visual Spacing (Gaps):** Maintain at least `15px` of spacing vertically and horizontally between adjacent visual blocks.
- **Visual Heights:**
  - **KPI Cards:** Height must be **at least `90px`** (recommended: `95px`). Anything below will cramp the text.
  - **Charts:** Height must be **at least `260px`** (recommended: `280px`) to prevent axis/legend overlaps.
  - **Tables:** Height must be **at least `220px`** (recommended: `240px`) to allow scroll-free visibility.
  - **Slicers:** Height must be **at least `100px`** (recommended: `110px`).

### KPI Card Styling Rules (No Overlapping Text):
- **Hide Category Label:** Always set `"categoryLabel"` properties: `show: false`.
- **Fail-safe Category Label Color Matching:** Set `"categoryLabel"` property `"color"` to the **exact same hex code as the card's background color**. This ensures that even if Power BI ignores the `show: false` instruction and renders the label, it remains completely invisible to the user.
- **Text Sizing:** Title size: `9pt` or `10pt`. Callout value size: `20pt` to `24pt`.

### Layout Validation Script:
Before compiling report pages, run a validation script to programmatically assert coordinate boundaries and prevent overlaps.
```python
# Check overlaps between any two visuals A and B
x_overlap = not (A.x + A.width <= B.x or B.x + B.width <= A.x)
y_overlap = not (A.y + A.height <= B.y or B.y + B.height <= A.y)
if x_overlap and y_overlap:
    raise ValueError("Visual overlap detected!")
```


