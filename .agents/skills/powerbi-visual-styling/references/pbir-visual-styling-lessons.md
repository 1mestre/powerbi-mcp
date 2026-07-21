# PBIR Visual Styling — Lessons Learned (NETFLIX Project)

> Hard-won lessons from debugging why PBID ignores visualContainerObjects, theme visualStyles, and color bindings. Documented so future agents don't repeat the same loop.

---

## Color Scheme — NETFLIX Project

| Purpose | Hex | Usage |
|---------|-----|-------|
| Canvas background | `#FFFFFF` | Report canvas |
| Card/container bg | `#1A4055` / `#113243` | visualContainerObjects.background |
| Primary accent (bars) | `#0080FF` | dataColors[0], themeColor: dataColor1 |
| Secondary accent | `#1C3388` | dataColors[1], themeColor: dataColor2 |
| Primary text (titles, values) | `#FFFFFF` | fontColor, labelColor |
| Secondary text (axes, labels) | `#94A3B8` | categoryLabelColor, axis labelColor |
| Gridlines | `#475569` | gridlineColor |
| Border | `#285468` | visualContainerObjects.border.color |

---

## 1. Theme JSON Format (visualStyles)

**In theme.json:** Plain values, NO `expr/Literal` wrapper.

```json
"visualStyles": {
  "barChart": {
    "*": {
      "categoryAxis": [{
        "labelColor": {"solid": {"color": "#94A3B8"}},
        "gridlineColor": {"solid": {"color": "#475569"}},
        "gridlineStyle": "dashed",
        "gridlineThickness": 0.5
      }],
      "valueAxis": [{
        "labelColor": {"solid": {"color": "#FFFFFF"}},
        "gridlineColor": {"solid": {"color": "#475569"}},
        "gridlineStyle": "dashed",
        "gridlineThickness": 0.5
      }],
      "dataLabels": [{
        "labelColor": {"solid": {"color": "#94A3B8"}}
      }],
      "dataPoint": [{
        "fill": {"solid": {"color": {"themeColor": "dataColor1"}}}
      }],
      "legend": [{
        "labelColor": {"solid": {"color": "#94A3B8"}}
      }]
    }
  },
  "card": {
    "*": {
      "cardLabels": [{
        "labelColor": {"solid": {"color": "#FFFFFF"}},
        "categoryLabelColor": {"solid": {"color": "#94A3B8"}},
        "fontSize": 20,
        "bold": true,
        "fontFamily": "Segoe UI Semibold"
      }]
    }
  }
}
```

---

## 2. visual.json Format (visualContainerObjects + objects)

**In visual.json:** Must use `expr/Literal` wrapper for PBID to parse.

```json
"visualContainerObjects": {
  "title": [{
    "properties": {
      "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}},
      "text": {"expr": {"Literal": {"Value": "'Total Títulos'"}}},
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A4055'"}}}}},
      "alignment": {"expr": {"Literal": {"Value": "'center'"}}},
      "fontSize": {"expr": {"Literal": {"Value": "12D"}}},
      "bold": {"expr": {"Literal": {"Value": "true"}}}
    }
  }],
  "subTitle": [{
    "properties": { "show": {"expr": {"Literal": {"Value": "false"}}} }
  }],
  "background": [{
    "properties": {
      "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1A4055'"}}}}},
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "transparency": {"expr": {"Literal": {"Value": "0D"}}}
    }
  }],
  "border": [{
    "properties": {
      "show": {"expr": {"Literal": {"Value": "true"}}},
      "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#285468'"}}}}},
      "radius": {"expr": {"Literal": {"Value": "8D"}}}
    }
  }]
},
"objects": {}
```

---

## 3. Schema Version Lock (CRITICAL)

`visual.json` `$schema` MUST match `report.json` `reportVersionAtImport.visual` (e.g., `2.9.0`).

```json
// report.json
"reportVersionAtImport": { "visual": "2.9.0", ... }

// visual.json
"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"
```

**Mismatch = PBID silently ignores visualContainerObjects/objects.**

---

## 4. Required Workflow (Every Time)

1. **Close PBID** completely
2. Edit theme.json (visualStyles + structural colors)
3. Edit all visual.json (visualContainerObjects + objects = {})
4. **Delete `cache.abf`** in semantic model `.pbi/`
5. Open PBID → validates schema → applies theme + container formatting

---

## 5. Pitfalls That Cost Hours

| ❌ Wrong | ✅ Correct |
|----------|------------|
| `identityValue` in selector.data | Use `scopeId` with `Comparison` or omit selector for theme-driven |
| Mixing theme format (plain) with visual.json format (expr/Literal) | Keep formats separate per file type |
| Forgetting `subTitle.show = false` | Always hide subtitle explicitly |
| Putting axis/legend in `visualContainerObjects` | Axis/legend in `objects` or theme `visualStyles` |
| `dataColor1` as string in visual.json | Use `ThemeDataColor` expression: `{"expr": {"ThemeDataColor": {"ColorId": 0, "Percent": 0}}}` |
| Not deleting `cache.abf` | Always delete before opening PBID |
| Schema version mismatch | Lock to report.json version |

---

## 6. Color Binding for Per-Category Bars

**Theme drives per-category colors automatically.** In theme.json:
- `dataColors: ["#0080FF", "#1C3388", ...]` — PBID assigns sequentially
- `visualStyles.barChart.dataPoint.fill.themeColor: "dataColor1"` — default for single-series
- Do NOT use `dataPoint` with selectors in visual.json for per-category — let theme handle it

---

## 7. Card Visual Specifics

```json
// theme.json visualStyles.card
"cardLabels": [{
  "labelColor": {"solid": {"color": "#FFFFFF"}},      // main number = white
  "categoryLabelColor": {"solid": {"color": "#94A3B8"}}, // subtitle = gray
  "fontSize": 20, "bold": true, "fontFamily": "Segoe UI Semibold"
}]

// visual.json visualContainerObjects
"background": [{ "color": "#1A4055", "show": true }]
"border": [{ "color": "#285468", "radius": 8, "show": true }]
"title": [{ "fontColor": "#FFFFFF", "text": "'Total Títulos'", ... }]
```

---

## 8. Slicer Specifics

```json
// theme.json visualStyles.slicer
"header": [{ "fontColor": "#FFFFFF", "fontSize": 12, "bold": true }]
"items": [{ "fontColor": "#94A3B8", "fontSize": 11 }]
"inputText": [{ "fontColor": "#FFFFFF" }]

// visual.json visualContainerObjects (same as cards)
"background": "#1A4055", "border": "#285468", "title": "white"
```

---

## 9. Donut Chart Specifics

```json
// theme.json visualStyles.donutChart
"legend": [{ "labelColor": "#94A3B8", "fontSize": 10 }]
"labels": [{ "labelColor": "#FFFFFF", "fontSize": 10 }]
"dataPoint": [{ "fill": { "themeColor": "dataColor1" } }]
```

---

## 10. HTML Content Visual

Custom visual type (GUID): `htmlContent443BE3AD55E043BF878BED274D3A6855`

```json
// theme.json
"htmlContent443BE3AD55E043BF878BED274D3A6855": { "*": {} }

// visual.json visualContainerObjects
"background": "#1A4055", "border": "#285468", "title": "white" (or hidden)
```
Note: HTML content itself rendered via DAX measure returning HTML string.