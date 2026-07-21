# Dark Theme Contrast in Power BI PBIR

## The Problem
When applying a dark theme to a PBIP project, chart labels, axis text, and data labels become invisible. This happens because Power BI's default text color for chart elements is `#252423` (near-black), which has zero contrast on dark page backgrounds.

## Root Cause
The theme JSON must include element-level color classes. Most custom themes only set `background` and `foreground`, which is sufficient for light themes but NOT for dark themes.

## Fix: Add Class-Level Colors to Theme JSON

### Required Properties for Dark Themes
```json
{
  "name": "CY26SU05",
  "background": "#0F3040",
  "foreground": "#F8FAFC",
  "tableAccent": "#A56F63",
  "firstLevelElements": "#F8FAFC",     ← Primary text (titles, labels, card values)
  "secondLevelElements": "#CBD5E1",    ← Axis labels, legends, category text
  "thirdLevelElements": "#334155",     ← Gridlines, borders, separators
  "fourthLevelElements": "#1E3A5F"     ← Visual card background tints
}
```

### Color Class Reference
| Class | Purpose | Default | Dark Theme Value |
|-------|---------|---------|-----------------|
| `firstLevelElements` | Primary text (titles, headers) | `#252423` (black) | `#F8FAFC` (white) |
| `secondLevelElements` | Secondary text (axis labels, legends) | `#605E5C` (gray) | `#CBD5E1` (light gray) |
| `thirdLevelElements` | Tertiary (gridlines, strokes) | `#F3F2F1` (light) | `#334155` (dark gray) |
| `fourthLevelElements` | Subtle fills | `#B3B0AD` | `#1E3A5F` (dark blue) |
| `background` | Page/visual bg | `#FFFFFF` | `#0F3040` |
| `foreground` | Primary accent text | `#111827` | `#F8FAFC` |

### Visual Background Strategy
Three approaches for visual card backgrounds on dark themes:

1. **Seamless (recommended):** Set visual background to exact page color (`#0F3040`), transparency=0
2. **Subtle card:** Slightly lighter (`#1A4055`), transparency=0  
3. **Transparent:** Transparency=100 (inherits page bg) — ONLY if `firstLevelElements` is set to light color

### Verification Checklist
- [ ] `firstLevelElements` is light (not default `#252423`)
- [ ] `secondLevelElements` is readable on bg (`CBD5E1` works)
- [ ] Page background (`page.json objects.background`) matches theme background
- [ ] Visual backgrounds use consistent shade (all same or all transparent)
- [ ] Cache.abf deleted before reopening PBID

## Per-Visual Explicit Text Colors (visual.json)

Theme inheritance is unreliable for some visual elements. Set these EXPLICITLY in each `visual.json` after creation:

### card (KPI Cards)
**Property path:** `visualContainerObjects` → `cardVisual`
```json
{
  "visualContainerObjects": {
    "title": [{"properties": {"fontColor": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}}],
    "cardVisual": [{
      "properties": {
        "calloutValueColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}},
        "calloutLabelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}
      }
    }],
    "categoryLabel": [{"properties": {"color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}}}]
  }
}
```

### barChart / columnChart
**Property paths:** `objects` → `categoryAxis`, `valueAxis`, `dataLabels`, `legend`
```json
{
  "objects": {
    "categoryAxis": [{"properties": {
      "labelColor": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}},
      "gridlineColor": {"expr": {"Literal": {"Value": "'#4B5563'"}}}
    }}],
    "valueAxis": [{"properties": {
      "labelColor": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}},
      "gridlineColor": {"expr": {"Literal": {"Value": "'#4B5563'"}}}
    }}],
    "dataLabels": [{"properties": {
      "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}
    }}],
    "legend": [{"properties": {"labelColor": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}
  },
  "visualContainerObjects": {
    "title": [{"properties": {"fontColor": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}}]
  }
}
```

### donutChart / pieChart
```json
{
  "objects": {
    "legend": [{"properties": {"labelColor": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}],
    "labels": [{"properties": {"labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}}}}]
  },
  "visualContainerObjects": {
    "title": [{"properties": {"fontColor": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}}]  
  }
}
```

### slicer
```json
{
  "objects": {
    "header": [{"properties": {"fontColor": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}}],
    "items": [{"properties": {"fontColor": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}}]
  },
  "visualContainerObjects": {
    "title": [{"properties": {"fontColor": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}}]
  }
}
```

## Common Text Contrast Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Text black/invisible on dark bg | `firstLevelElements` not set in theme | Add `"firstLevelElements": "#F8FAFC"` to theme JSON |
| Card labels gray, hard to read | `calloutLabelColor` not set explicitly | Set `calloutLabelColor` in `cardVisual` object |
| Slicer items black on dark bg | `items.fontColor` not set | Add `items.fontColor` in slicer `objects` |
| Data labels gray on charts | `dataLabels.labelColor` not set | Add `labelColor` to `dataLabels` in chart objects |
| Axis labels black | `categoryAxis.labelColor` / `valueAxis.labelColor` not set | Add both axis label colors |
