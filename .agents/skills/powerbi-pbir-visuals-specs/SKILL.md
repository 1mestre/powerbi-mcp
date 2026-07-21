---
name: powerbi-pbir-visuals-specs
description: Specifications, valid visualType identifiers, projection bindings, queryState schemas, and objects styling for PBIR visual.json files.
---

# Power BI PBIR Visual Specifications & JSON Schemas

Use this skill when defining, structuring, formatting, or styling `visual.json` files for Power BI Projects (PBIR 2.0.0+ / page 2.x.x format).

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
* **Advanced & Custom Analytics:**
  - `"scatterChart"` (scatter / bubble plot)
  - `"slicer"` (slicer controls)
  - `"pythonVisual"` (Python visual using Matplotlib/Seaborn/Pandas)
  - `"rVisual"` (R visual using ggplot2/lattice/base R)

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

* **Page Folder Names:** Page folders under `pages/` must be named using 20-character lowercase hexadecimal strings or GUIDs. Do not use descriptive names.
* **NO `visualContainers` in page.json (page schema 2.1.0):** The page schema 2.1.0 does NOT support a `visualContainers` array. Visuals are auto-discovered from the `visuals/` subdirectory. Do NOT add `visualContainers` to `page.json` — it will cause a schema validation error: *"Se ha incluido una propiedad 'visualContainers' adicional en la propiedad root"*.

---

## 3. Projection Bindings by Chart Type (queryState Schema)

Map fields inside `visuals/{visual-name}/visual.json` under `visual.query.queryState`.

### Mandatory Projection Keys
Every field projection inside the `"projections": [...]` array must contain `"queryRef"` and `"nativeQueryRef"` as string values. Failing to include these strings will cause a report load crash.

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

### Grouped Charts & Measure References
Grouped charts (e.g., `treemap`, `funnel`, `barChart`, `columnChart`, `pieChart`, `donutChart`, `lineChart`) **DO NOT accept direct columns (`"Column"`) in their values projection (`Y` or `Values`)**. Point to DAX measures using `"Measure"`:
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
**Schema Version Lock (CRITICAL):** All `visual.json` files **MUST** use schema version `2.9.0` to match the `visual: "2.9.0"` declared in `report.json` (`reportVersionAtImport`). Using `2.10.0` or any other version causes PBID to silently ignore the visual — it renders with defaults, no error shown.
```json
"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"
```
Validate: `grep -r '"\$schema"' Report/definition/pages/*/visuals/*/visual.json | grep -v 2.9.0`

---

## 4. Valid JSON Keys & Position

In modern `visualContainer` files, never write a `"size"`, `"config"`, or `"filters"` property on the root object of `visual.json`. Width and height must reside strictly inside `"position"`:
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

---

## 5. `objects` vs `visualContainerObjects` — STRICT SEPARATION (CRITICAL)

These two sections serve different purposes and mixing them causes schema validation errors:

- **`objects`** — Chart-level and visual-level styling properties. This is where you put:
  - **Axis properties:** `categoryAxis`, `valueAxis`, `y2Axis`
  - **Legend/Labels:** `legend`, `labels`, `dataLabels`, `categoryLabel`
  - **Slicer settings:** `general` (with `responsive`), `items` (with `orientation`, `singleSelect`, `fontSize`, etc.)
  - **Data point colors:** `dataPoint`
  - **Grid/Plot settings:** `plotArea`, `grid`, `lineStyles`
  - **Series formatting:** `seriesLabels`, `fillPoint`, `bubbles`

- **`visualContainerObjects`** — Container-level properties only. Must be INSIDE `visual` block (not root of `visual.json`). This is strictly for:
  - `title` (show, text, fontColor)
  - `background` (show, color, transparency)
  - `border` (show, color, width)
  - `outline`, `divider` (card-specific)

### ❌ WRONG (causes schema error):
```json
"visualContainerObjects": {
  "title": [{ "properties": { ... } }],
  "categoryAxis": [{ "properties": { ... } }]  // ERROR: belongs in objects
}
```

### ✅ CORRECT:
```json
{
  "visual": {
    "visualType": "barChart",
    "objects": {
      "categoryAxis": [{ "properties": { ... } }],
      "valueAxis": [{ "properties": { ... } }]
    },
    "visualContainerObjects": {
      "title": [{ "properties": { "show": { "expr": { "Literal": { "Value": "true" } } }, "text": { "expr": { "Literal": { "Value": "'My Chart'" } } } } }]
    }
  }
}
```
*(Note: `"title"` is valid in BOTH `objects` and `visualContainerObjects`, but prefer `visualContainerObjects` for title because it follows the modern visualContainer schema).*

---

## 6. Visual Customization & Component Styling

### Formatting and Titles in visual.json
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

### KPI Cards (Classic Card Visuals)
To style cards with solid backgrounds and white callout text:
- **Hide Category Label:** Target the `"categoryLabels"` object (not `"labels"`):
  ```json
  "categoryLabels": [
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
To override default theme colors for individual slices (e.g., coloring specific values like 'Amazon' or 'Merchant'), use `"dataPoint"` with a series selector using `scopeId` and a `Comparison` expression (never use raw `queryRef` or `value` under `data[0]`):
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

### Column & Line Chart Series Coloring (Theme-Aware Color Binding)
To ensure visuals pick up the colors defined in your active report theme JSON automatically, use `"ThemeDataColor"` expressions instead of `"Literal"` hex strings:

- **Column Chart (using `"fill"` and `"ThemeDataColor"`):**
  ```json
  "objects": {
    "dataPoint": [
      {
        "properties": {
          "fill": {
            "solid": {
              "color": {
                "expr": {
                  "ThemeDataColor": {
                    "ColorId": 2,
                    "Percent": 0
                  }
                }
              }
            }
          }
        }
      }
    ]
  }
  ```
- **Line Chart (using `"fillColor"` and `"ThemeDataColor"`):**
  ```json
  "objects": {
    "dataPoint": [
      {
        "properties": {
          "fillColor": {
            "solid": {
              "color": {
                "expr": {
                  "ThemeDataColor": {
                    "ColorId": 1,
                    "Percent": 0
                  }
                }
              }
            }
          }
        }
      }
    ]
  }
  ```

---

## 7. Python & R Visual Specifications (`pythonVisual` & `rVisual`)

Python and R script visuals allow embedding custom Matplotlib/Seaborn and R `ggplot2` code directly into PBIR `visual.json` files.

### 7.1 Python Visual Schema (`pythonVisual`)
- **`visualType`:** `"pythonVisual"`
- **Fields / Projections:** Defined in `visual.query.queryState.Values.projections`. Fields become columns in the Python `dataset` DataFrame.
- **`objects.script`:** Specifies `scriptProvider: 'python'` and `scriptSource` containing the Python code.

```json
{
  "visual": {
    "visualType": "pythonVisual",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "amazon_clean" } }, "Property": "actual_price" } },
              "queryRef": "amazon_clean.actual_price",
              "nativeQueryRef": "actual_price"
            }
          ]
        }
      }
    },
    "objects": {
      "script": [
        {
          "properties": {
            "scriptProvider": { "expr": { "Literal": { "Value": "'python'" } } },
            "scriptSource": { "expr": { "Literal": { "Value": "'import matplotlib.pyplot as plt\\nimport seaborn as sns\\nfig, ax = plt.subplots()\\nsns.heatmap(dataset.corr(), ax=ax)\\nplt.show()'" } } }
          }
        }
      ]
    }
  }
}
```

### 7.2 R Visual Schema (`rVisual`)
- **`visualType`:** `"rVisual"`
- **Fields / Projections:** Defined in `visual.query.queryState.Values.projections`. Fields become columns in the R `dataset` data frame.
- **`objects.script`:** Specifies `scriptProvider: 'r'` and `scriptSource` containing the R code.

```json
{
  "visual": {
    "visualType": "rVisual",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": { "Column": { "Expression": { "SourceRef": { "Entity": "amazon_clean" } }, "Property": "rating" } },
              "queryRef": "amazon_clean.rating",
              "nativeQueryRef": "rating"
            }
          ]
        }
      }
    },
    "objects": {
      "script": [
        {
          "properties": {
            "scriptProvider": { "expr": { "Literal": { "Value": "'r'" } } },
            "scriptSource": { "expr": { "Literal": { "Value": "'library(ggplot2)\\np <- ggplot(dataset, aes(x=rating)) + geom_histogram()\\nprint(p)'" } } }
          }
        }
      ]
    }
  }
}
```

### 7.3 Multi-Page Registration Workflow
When adding new report pages (e.g. `page_advanced_analytics`):
1. Create subfolder `pages/{page_name}/` and `page.json` (schema `page/2.1.0/schema.json`, canvas 1280x980, background color without `show` property).
2. Append `{page_name}` to `pages.json` under `pageOrder`.
3. Create `visuals/{visual_name}/visual.json` for each visual in the page.

---

## 🔗 RELATED SKILLS & REPOSITORY FILES

- 🏠 **[powerbi-orchestrator](file:///C:/Users/Sebas/AppData/Local/hermes/skills/powerbi/powerbi-orchestrator/SKILL.md)** - Master Skill Hub
- 🎨 **[powerbi-design-layout-themes](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-design-layout-themes/SKILL.md)** - Canvas Grid & ThemeDataColor Palette Mapping
- 🔧 **[powerbi-pbir-troubleshooting](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-troubleshooting/SKILL.md)** - Troubleshooting PBID rewrite behaviors and JSON syntax errors
- 📈 **[create_dashboard.py](file:///C:/Users/Sebas/desktop-ssas-mcp/create_dashboard.py)** - Interactive Plotly dashboard and SSAS DAX query integration
