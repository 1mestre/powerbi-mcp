# NETFLIX Dark-Theme Retrofitting — Session Reference

**Date:** 2026-07-21
**Project:** `F:\powerbi proyects\NETFLIX\`
**Theme:** CY26SU05 (Slate & Terracotta)
**Page bg:** #0F3040

## Visuals Modified (7)

| Visual | Type | What was added |
|--------|------|----------------|
| `bar_paises` | barChart | bg #1A4055, border, categoryAxis/valueAxis colors, title fontColor, 10 dataPoints (theme colors cycled with Percent=0) |
| `bar_anios` | barChart | bg #1A4055, border, categoryAxis/valueAxis colors, title fontColor |
| `donut_tipo` | donutChart | bg #1A4055, border, legend fontColor, title fontColor |
| `kpi_total_titulos` | card | bg #1A4055, border, labels color (F8FAFC), title fontColor |
| `kpi_total_peliculas` | card | bg #1A4055, border, labels color (F8FAFC), title fontColor |
| `kpi_total_series` | card | bg #1A4055, border, labels color (F8FAFC), title fontColor |
| `slicer_tipo` | slicer | bg #1A4055, border, items fontColor + background |

## Script used for bulk update

`fix_visuals.py` — Python script that loaded each visual.json, modified data in memory (json module), and wrote back with `json.dump(data, f, indent=2, ensure_ascii=False)`. Key technical detail: used `data.get("visual", data)` to handle both structures where `visual` is a nested key vs the root (slicer had visual as root).

## Color Palette Used

```python
FOREGROUND = "#F8FAFC"
GRIDLINE = "#4B5563"
CARD_BG = "#1A4055"      # Opaque card bg — lighter than page bg #0F3040
BORDER_COLOR = "#285468"  # Subtle visible edge
```

## Key Learnings

1. **Background transparency:** `show: true` + `transparency: 0D` makes the visual bg fully opaque. Without `show: true`, transparency may not render.
2. **Title fontColor:** Must be set inside `visualContainerObjects.title[0].properties.fontColor` — the theme foreground doesn't automatically apply to titles.
3. **Card callout values:** Controlled via `objects.labels`, NOT `objects.dataLabels`.
4. **Slicer items:** Need both `fontColor` and `background` in `objects.items` for dark theme.
5. **dataPoint Percent:** `Percent: 0` = full color, `Percent: 20` = tinted lighter, `Percent: -20` = shaded darker. Percent=0 should be explicit.
6. **D suffix:** All numeric literals in PBIR require `D` suffix (e.g., `"0D"`, `"8D"`, `"28D"`).
