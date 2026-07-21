# Anti-Gravity 5 Pilares — Framework Anti-Bucles para PBIR

Documento derivado de la sesión con Anti-Gravity (resolvió el formateo visual que falló en 5 iteraciones previas). Incluye correcciones críticas al skill `powerbi-visual-styling`.

---

## 🟢 Pilar 1: Binding Programático de Visuales Custom (AppSource)

**Causa del fallo:** Los visuales de terceros (`publicCustomVisuals`) en PBIR ignoran la proyección si en `queryState` solo se incluye `"Values"`. La mayoría usa un rol interno específico de su manifiesto (p. ej., `"content"` para HTML Content).

**Regla para el agente:** Al generar un `visual.json` para un visual custom, duplicar la proyección en `queryState` bajo la clave `"Values"` y la clave específica del rol (`"content"`).

```json
"queryState": {
  "Values": { "projections": [...] },
  "content": { "projections": [...] }  // dual projection REQUIRED
}
```

---

## 🟢 Pilar 2: Fondo del Lienzo (Canvas) vs Tema JSON

**Causa del fallo:** `visualStyles.page.background` dentro de un archivo de tema JSON es ignorado por el motor de renderizado PBIR para el lienzo principal.

**Regla para el agente:** Para cambiar el color del lienzo (p. ej. a Blanco `#FFFFFF` o Azul Marino `#0F3040`), editar `page.json` directamente en `objects.background`:

```json
"background": [{
  "properties": {
    "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#0F3040'" } } } } },
    "transparency": { "expr": { "Literal": { "Value": "0D" } } }
  }
}]
```

**Nota:** `page.json` NO acepta la propiedad `show`; incluirla lanza un error de esquema.

---

## 🟢 Pilar 3: Mapeo Estricto de Claves de Color por Tipo de Visual

**Causa del fallo:** Usar nombres genéricos como `"color"` o `"labelColor"` en visuales incorrectos hace que Power BI ignore la propiedad y recurra al color por defecto (que con `ColorId: 0` resuelve a blanco o gris sin contraste).

**Regla para el agente — Tabla Maestra:**

| Visual Type | Clave Correcta | Error Común |
|-------------|----------------|-------------|
| **Tarjeta KPI Clásica (`card`)** | La cifra grande se formatea en `"labels"` (con propiedad `"color"`). El subtítulo inferior se oculta en `"categoryLabels"` (plural, con `"show": false`). | Usar `"dataLabels"` o `"categoryLabel"` (singular) → sin efecto |
| **Donut / Pie Chart (`donutChart`)** | El texto de las llamadas de porcentaje con flecha se ajusta en `"labels"` usando `"color": "'#FFFFFF'"`. | Usar `"dataLabels"` → no funciona |
| **Barras (`barChart` / `columnChart`)** | El color de los textos de la escala es `"labelColor"`, y el título del eje es `"titleColor"` (o `"showTitle": false` para ocultar la etiqueta de campo redundante). | Usar `"fontColor"` → ignorado |

---

## 🟢 Pilar 4: Forzar Barras Multicolor en Gráficos de Barras (`scopeId` Selectors)

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

---

## 🟢 Pilar 5: Rejilla 1280x720 y Márgenes de Seguridad (Anti-Apiñamiento)

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

---

## 📦 visualContainerObjects vs objects — Separación Estricta (Actualizado)

| Sección | Claves Válidas | Prohibido |
|---------|----------------|-----------|
| **visualContainerObjects** | `title`, `subTitle`, `background`, `border`, `visualTooltip`, `dropShadow`, `visualHeader`, `visualHeaderTooltip`, `stylePreset` | `legend`, `categoryAxis`, `valueAxis`, `dataPoint`, `dataLabels`, `labels`, `header`, `items`, `inputText`, `cardLabels`, `fillRule`, `defaultColor` |
| **objects** | `categoryAxis`, `valueAxis`, `legend`, `labels`, `dataLabels`, `dataPoint`, `cardLabels`, `categoryLabels`, `header`, `items`, `inputText`, `general` (slicer) | `title`, `background`, `border`, `subTitle`, `visualTooltip`, `dropShadow` |

### Reglas por Tipo de Visual:

| Visual | `visualContainerObjects` | `objects` |
|--------|-------------------------|-----------|
| **card (KPI)** | `background`, `border`, `radius` (8D), `title` | `labels` (value, white), `categoryLabels` (show:false) |
| **donutChart** | `title`, `background`, `border` | `labels` (white), `legend` (light gray) |
| **barChart / columnChart** | `title`, `background`, `border` | `categoryAxis`, `valueAxis`, `dataPoint` (con `scopeId` para multicolor) |
| **slicer** | `title`, `background`, `border` | `header` (show:false), `items` (fontColor, fontSize), `inputText` (fontColor) — **NO `orientation` en `general`** |
| **htmlContent...** | `title`, `background`, `border` | `{}` (empty) — dual projection `Values` + `content` requerida |

---

## ⚠️ Correcciones Críticas a Errores Previos del Skill

1. **Slicer `general.orientation`**: NUNCA agregar `"orientation": "'vertical'"` dentro de `general` en el slicer. En el esquema PBIR, poner `orientation` bajo `general` corrompe la estructura y deja el cuadro en blanco sin checkboxes. Configurar estrictamente: `header.show:false`, `items.fontColor/fontSize`, `visualContainerObjects` con título/fondo/borde.

2. **page.json background**: NO incluir propiedad `show`. Incluirla lanza error de esquema. Solo `color` + `transparency`.

3. **HTML Content visual**: Requiere proyección dual `"Values"` Y `"content"` en `queryState` para auto-bind al abrir PBID.

4. **Card KPIs**: Fondo y borde en `visualContainerObjects`; `objects` SOLO `labels` + `categoryLabels`.

5. **Schema 2.9.0 lock**: Todos los `visual.json` DEBEN usar `$schema` coincidente con `report.json` (`"visual": "2.9.0"`). Mismatch → PBID ignora visual silenciosamente.

---

## 📋 Checklist Pre-Ejecución (Anti-Bucles)

- [ ] `report.json` → leer `"visual": "2.9.0"` → setear `$schema` en TODOS los visual.json
- [ ] `page.json` → `background.color = '#0F3040'` (sin `show`)
- [ ] KPIs (3): `visualContainerObjects` con fondo/borde, `objects` = `labels` + `categoryLabels`
- [ ] Slicer: `objects.header.show:false`, `objects.items.fontColor/fontSize`, NO `orientation`
- [ ] Donut: `objects.labels.color=white`, `objects.legend.labelColor=light gray`
- [ ] Barras: `objects.dataPoint` con array de `scopeId` selectors para multicolor
- [ ] HTML: `queryState` con `Values` + `content` dual
- [ ] Borrar `cache.abf` antes de abrir PBID
- [ ] Validar: `python validate_pbip.py netflix.pbip` → 51+/54 OK