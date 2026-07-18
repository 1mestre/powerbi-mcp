---
name: powerbi-pbir-editor
description: Guidelines and schemas for programmatically creating Power BI visuals in PBIR JSON format and editing TMDL measure files.
---

# Power BI PBIR & TMDL Developer Skill

Use this skill when you need to programmatically add or modify visuals in a Power BI Project (PBIP/PBIR format) or append DAX measures to Tabular Model Definition Language (TMDL) files.

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
* **TMDL Comments (CRITICAL):** TMDL only supports `//` for single-line comments. **NEVER use `--` (SQL-style double-dash)** — the TMDL parser will throw `InvalidLineType: Other` at the comment line. Power BI Desktop will fail to load with *"Error de formato TMDL: Tipo de línea inesperado: Other"*. If you must comment, omit comments entirely or use `//`.
* **discourageImplicitMeasures Setting (CRITICAL):** If the model defines any Calculation Group (`calculationGroup`), you **MUST** set the property `discourageImplicitMeasures: true` under `model Model` in `model.tmdl`. Failure to do so will result in a load crash in Power BI Desktop.
* **Avoid isKey on Dimensions (CRITICAL):** Do not add `isKey: true` to primary key columns of standard import tables (like date or dimension tables). It can cause *"a cyclic reference was found during evaluation"* errors in Power Query. Use model-level relationships to map the keys.
  - **Transient Evaluation Cache Bug:** Even when the model schema is 100% correct, Power BI Desktop may occasionally display a false-positive *"Se encontró una referencia cíclica durante la evaluación"* (A cyclic reference was found during evaluation) error on first open or first refresh due to a corrupted memory cache in the engine. This is a known Power BI bug. **Solution:** Tell the user to simply click the **Actualizar (Refresh)** button a second time, or close and reopen Power BI Desktop. The second load always completes successfully.
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
* **NO `visualContainers` in page.json (page schema 2.1.0):** The page schema 2.1.0 does NOT support a `visualContainers` array. Visuals are auto-discovered from the `visuals/` subdirectory. Do NOT add `visualContainers` to `page.json` — it will cause a schema validation error: *"Se ha incluido una propiedad 'visualContainers' adicional en la propiedad root"*.
* **`objects` vs `visualContainerObjects` — STRICT SEPARATION (CRITICAL):** These two sections serve different purposes and mixing them causes schema validation errors:
  - **`objects`** — Chart-level and visual-level styling properties. This is where you put:
    - **Axis properties:** `categoryAxis`, `valueAxis`, `y2Axis`
    - **Legend/Labels:** `legend`, `labels`, `dataLabels`, `categoryLabel`
    - **Slicer settings:** `general` (with `responsive`), `items` (with `orientation`, `singleSelect`, `fontSize`, etc.)
    - **Data point colors:** `dataPoint`
    - **Grid/Plot settings:** `plotArea`, `grid`, `lineStyles`
    - **Series formatting:** `seriesLabels`, `fillPoint`, `bubbles`
  - **`visualContainerObjects`** — Container-level properties only. This is strictly for:
    - `title` (show, text, fontColor)
    - `background` (show, color, transparency)
    - `border` (show, color, width)
    - `outline`, `divider` (card-specific)
  - **WRONG** (causes schema error):
    ```json
    "visualContainerObjects": {
      "title": [{ "properties": { ... } }],
      "categoryAxis": [{ "properties": { ... } }]  // ERROR: belongs in objects
    }
    ```
  - **CORRECT:**
    ```json
    "objects": {
      "categoryAxis": [{ "properties": { ... } }],
      "valueAxis": [{ "properties": { ... } }]
    },
    "visualContainerObjects": {
      "title": [{ "properties": { "show": { "expr": { "Literal": { "Value": "true" } } }, "text": { "expr": { "Literal": { "Value": "'My Chart'" } } } } }]
    }
    ```
  - **Exception:** `"title"` is valid in BOTH `objects` and `visualContainerObjects`, but prefer `visualContainerObjects` for title because it follows the modern visualContainer schema.

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

### Column & Line Chart Series Coloring (Theme-Aware Color Binding)
To ensure visuals pick up the colors defined in your active report theme JSON automatically (and do not hardcode manual formatting overrides), use `"ThemeDataColor"` expressions instead of `"Literal"` hex strings:

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
  Where `ColorId` is the 0-based index of the color in the report theme's `dataColors` array (e.g., `0` is the first color, `1` is the second, etc.).

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

### KPI Card Styling Rules (Zero Crop Guarantee & Clean Typography):
- **Card Height Standard:** Height must be **at least `100px`** to ensure full vertical breathing room for callout values and titles.
- **Hide Category Label (Zero-Crop Fail-safe):** Always set `"categoryLabel"` properties:
  - `"show"`: `false`
  - `"fontSize"`: `1` (1pt font size so it occupies 0 vertical space)
  - `"transparency"`: `100` (100% transparent)
  - `"color"`: Set to the **exact same hex code as the card's background color**.
- **Text Sizing & Alignment:** Title size: `9pt` or `10pt` (`fontColor`: `#F8FAFC` or `#111827`). Callout value size: `22pt`.

### Layout Validation Script:
Before compiling report pages, run a validation script to programmatically assert coordinate boundaries and prevent overlaps.
```python
# Check overlaps between any two visuals A and B
x_overlap = not (A.x + A.width <= B.x or B.x + B.width <= A.x)
y_overlap = not (A.y + A.height <= B.y or B.y + B.height <= A.y)
if x_overlap and y_overlap:
    raise ValueError("Visual overlap detected!")
```

---

## 9. WCAG Contrast Ratios & Executive Design Architecture (Visual Harmony)
To ensure reports look clean, high-contrast, professional, and visually unified across all Power BI themes:

### 1. WCAG 2.1 AA Contrast Ratio Standard:
- **Contrast Formula:** $CR = \frac{L_1 + 0.05}{L_2 + 0.05} \ge 4.5:1$ for body/title text and $\ge 3.0:1$ for large text/KPI callout numbers.
- **Power BI ThemeDataColor Mapping (CRITICAL):**
  - **`ColorId: 0`**: Maps to the active theme's **Background** color (White `#FFFFFF` in light themes, Slate `#0F172A` in dark themes).
  - **`ColorId: 1`**: Maps to the active theme's **Foreground** text color (Dark Slate `#111827` / Dark Vino `#92003A` in light themes, Ice White `#F8FAFC` in dark themes).
  - **`ColorId: 2, 3, etc.`**: Map to Theme Data Colors (Data Colors array).
- **Contrast Rules (GUARANTEED):**
  - Card/Container backgrounds must always use **`ColorId: 0`** (which automatically matches the canvas theme).
  - Card/Container titles must always use **`ColorId: 1`** (which dynamically switches to high-contrast dark text in light mode and white text in dark mode).
  - Callout numbers must use **`ColorId: 1`, `2`, or `3`** (never `0` on light themes, or any color that has a low contrast ratio against the background).
  - **NEVER** place white text (`ColorId: 0` on light themes) on light backgrounds.
- **Verification Rule:** If changing themes, check that no elements map to `ColorId: 0` for text in light mode.

### 2. Container Homogeneity Principle:
- **Unified Visual Containers:** All visual containers on a dashboard page (KPI Cards, Charts, Tables, Slicers) MUST share a single, homogeneous background container specification (e.g. Pure White `#FFFFFF` background with `0%` transparency and subtle `1px` border `#E5E7EB`).
- **Avoid "Patchwork" Designs:** Do not mix solid dark purple cards next to white donut charts and black KPI boxes. A patchwork of mismatched container backgrounds creates visual clutter and looks amateurish.

### 3. Data Accentuation vs Container Neutrality:
- Use colors purposefully for **data accentuation** (e.g. KPI callout value numbers, chart bars, line series, donut slices), while maintaining clean, neutral, high-contrast framing for containers and titles.

---

## 10. Operational Traps & Field-Proven Fixes (Amazon Dashboard After-Action)

### 10.1 UTF-8 WITHOUT BOM (CRITICAL FOR PBIP LOAD)
Power BI Project (PBIP) requires ALL JSON files to be **UTF-8 encoded WITHOUT Byte Order Mark (BOM)**. PowerShell 5.1 `Set-Content -Encoding UTF8` adds a BOM, which causes PBID to crash on open with: *"Only text with UTF8 encoding without BOM is supported. Detected BOM: 'UTF-8'"*.
**Fix:** Use .NET directly:
```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
```

### 10.2 AVOID `%` IN MEASURE NAMES
The `%` character in DAX measure names (even inside TMDL single quotes) causes grouped charts (columnChart, barChart, etc.) to render as **empty rectangles**. Power BI's internal engine interprets the `%` as a modulus operator or format specifier rather than a literal character.
**Fix:** Use `Pct` instead of `%` in all measure names:
- `measure 'Avg Discount %'` -> `measure 'Avg Discount Pct'`

### 10.3 NO `dataPoint` ON TREEMAP
Treemaps use the theme's `dataColors` palette across all categories automatically. Adding `objects.dataPoint` with a single `ThemeDataColor` overrides all rectangles to one color. Using `ColorId: 0` sets them to the **background color** (`#F7F5F2`), making them invisible.
**Fix:** Do NOT include `dataPoint` in treemap objects. Use `"objects": {}`.

### 10.4 KPI Card Minimum Setup (Zero-Crop)
Every KPI card MUST include:
- **`objects.categoryLabel`** with `show: false`, `fontSize: 1`, `transparency: 100`
- **`objects.labels`** with `color: #FFFFFF`, `fontSize: 28`
- **`visualContainerObjects.background`** with solid dark color, `show: true`
- **`visualContainerObjects.title`** with `show: true`, `fontColor: #F8FAFC`

### 10.5 All Charts Need Explicit Container Background
Charts render transparent on the page unless `visualContainerObjects` includes a `background` and `border` block with explicit `#FFFFFF` background.

### 10.6 Canvas Height Budget (1280x1000)
Use **1280x1000** when the layout includes: 1 slicer row (110px) + 4 KPI cards (110px) + 2 chart rows (290px each) + bottom row (110px) = 1000px with 15px gaps.

### 10.7 `queryRef` / `nativeQueryRef` with Spaces
Measures with spaces use dot-notation without brackets:
```json
"queryRef": "amazon_clean.Total Products",
"nativeQueryRef": "Total Products"
```

---
## 11. Premium Theme Catalogue (Modos Claro y Oscuro)
These pre-configured themes are designed to enforce perfect readability and contrast standards while projecting distinct, premium vibes:

### 1. 🌸 **"Magenta Blossom" (Modo Claro)**
- **Palette**: `#92003A` (Vino oscuro), `#F62477` (Rosa brillante), `#FFADEE` (Rosa pastel), `#FFE185` (Arena suave).
- **Application**: Pure white canvas with soft sand card backgrounds. Vino/Magenta for high-contrast titles and text.

### 2. 🌌 **"Slate & Terracotta" (Modo Oscuro)**
- **Palette**: `#0F3040` (Slate Azul Oscuro), `#464858` (Gris Asfalto), `#A56F63` (Terracota), `#D99B7F` (Terracota claro).
- **Application**: Deep slate blue canvas with dark slate card surfaces. Light terracotta for text and callouts.

### 3. 🌿 **"Ecotone Spring" (Modo Claro)**
- **Palette**: `#769826` (Oliva), `#A1CB35` (Verde primavera), `#FFDE4E` (Amarillo), `#FF9D4D` (Naranja).
- **Application**: Clean light grey canvas, white containers, olive text, vibrant green/yellow/orange data series.

### 4. ☕ **"Roasted Espresso" (Modo Oscuro)**
- **Palette**: `#60241E` (Marrón Espresso), `#95271D` (Marrón rojizo), `#B34A44` (Marrón), `#E77B49` (Tono arcilla claro).
- **Application**: Dark espresso canvas, reddish-brown containers, light clay text for high contrast.

### 5. ❄️ **"Vintage Nordic" (Modo Claro)**
- **Palette**: `#0B1849` (Marino), `#124D1C` (Pino), `#E4B028` (Oro viejo), `#EBEDE3` (Gris pálido).
- **Application**: Pale nordic grey canvas, white containers, deep navy text, pine green and gold accents.




