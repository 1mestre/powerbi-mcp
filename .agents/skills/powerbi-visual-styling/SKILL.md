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

## 🎯 5 Pilares del Framework Anti-Gravity (Reglas Obligatorias)

Estos 5 pilares evitan bucles infinitos de corrección al trabajar con PBIP/PBIR. **Inclúyelos en el prompt del agente** para ejecución determinista:

### 🟢 Pilar 1: Binding Programático de Visuales Custom (AppSource)
**Causa del fallo:** Los visuales de terceros (`publicCustomVisuals`) en PBIR ignoran la proyección si en `queryState` solo se incluye `"Values"`. La mayoría usa un rol interno específico de su manifiesto (p. ej., `"content"` para HTML Content).
**Regla para el agente:** Al generar un `visual.json` para un visual custom, duplicar la proyección en `queryState` bajo la clave `"Values"` y la clave específica del rol (`"content"`).

### 🟢 Pilar 2: Fondo del Lienzo (Canvas) vs Tema JSON
**Causa del fallo:** `visualStyles.page.background` dentro de un archivo de tema JSON es ignorado por el motor de renderizado PBIR para el lienzo principal.
**Regla para el agente:** Para cambiar el color del lienzo (p. ej. a Blanco `#FFFFFF`), editar `page.json` directamente en `objects.background`:
```json
"background": [{
  "properties": {
    "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#FFFFFF'" } } } } },
    "transparency": { "expr": { "Literal": { "Value": "0D" } } }
  }
}]
```
(Nota: `page.json` no acepta la propiedad `show`; incluirla lanza un error de esquema).

### 🟢 Pilar 3: Mapeo Estricto de Claves de Color por Tipo de Visual
**Causa del fallo:** Usar nombres genéricos como `"color"` o `"labelColor"` en visuales incorrectos hace que Power BI ignore la propiedad y recurra al color por defecto (que con `ColorId: 0` resuelve a blanco o gris sin contraste).
**Regla para el agente:**
| Visual Type | Clave Correcta | Error Común |
|-------------|----------------|-------------|
| **Tarjeta KPI Clásica (`card`)** | La cifra grande se formatea en `"labels"` (con propiedad `"color"`). El subtítulo inferior se oculta en `"categoryLabels"` (plural, con `"show": false`). | Usar `"dataLabels"` o `"categoryLabel"` (singular) → sin efecto |
| **Donut / Pie Chart (`donutChart`)** | El texto de las llamadas de porcentaje con flecha se ajusta en `"labels"` usando `"color": "'#FFFFFF'"`. | Usar `"dataLabels"` → no funciona |
| **Barras (`barChart` / `columnChart`)** | El color de los textos de la escala es `"labelColor"`, y el título del eje es `"titleColor"` (o `"showTitle": false` para ocultar la etiqueta de campo redundante). | Usar `"fontColor"` → ignorado |

### 🟢 Pilar 4: Forzar Barras Multicolor en Gráficos de Barras (`scopeId` Selectors)
**Causa del fallo:** Asignar un solo objeto a `objects.dataPoint` provoca que todas las barras se pinten monocromáticas.
**Regla para el agente:** Para forzar colores distintos por barra, inyectar un array en `objects.dataPoint` usando selectores `scopeId` de comparación. La propiedad `"Right"` dentro de `"Comparison"` **NO debe llevar wrapper `"expr"` externo**:
```json
"dataPoint": [
  {
    "properties": { "fill": { "solid": { "color": { "expr": { "Literal": { "Value": "'#E50914'" } } } } } },
    "selector": {
      "metadata": "tabla.columna",
      "data": [{
        "scopeId": {
          "Comparison": {
            "ComparisonKind": 0,
            "Left": { "Column": { "Expression": { "SourceRef": { "Entity": "tabla" } }, "Property": "columna" } },
            "Right": { "Literal": { "Value": "'ValorCategoria'" } }
          }
        }
      }]
    }
  }
]
```

### 🟢 Pilar 5: Rejilla 1280x720 y Márgenes de Seguridad (Anti-Apiñamiento)
**Causa del fallo:** Asignar anchos o coordenadas x continuas sin espacio provoca colapso visual o encimado.
**Regla para el agente:**
- **Dimensiones de referencia:** Lienzo estándar `1280 x 720` (o `1280 x 920`).
- **Márgenes de lienzo:** Mínimo `20px` a los bordes (`x=20`, `y=20`).
- **Brecha inter-visual (Gap):** Mínimo `20px` entre bloques contiguos (si un KPI mide `w=280` y empieza en `x=20`, el siguiente debe empezar en `x = 20 + 280 + 20 = 320`).
- **Altura mínima:** KPIs y Slicers `h >= 100px`; Gráficos `h >= 260px`.

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
