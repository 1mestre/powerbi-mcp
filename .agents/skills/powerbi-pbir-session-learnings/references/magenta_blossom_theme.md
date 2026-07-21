# Magenta Blossom Theme — Complete Specification

**Selected by user for YouTube dashboard (marketing/social media data)**

## Color Palette
```json
{
  "name": "CY26SU05",
  "dataColors": [
    "#92003A",  // Dark Wine (primary)
    "#F62477",  // Bright Magenta (secondary)
    "#FFADEE",  // Pastel Pink (tertiary)
    "#FFE185",  // Soft Sand (quaternary)
    "#3B82F6",  // Blue
    "#10B981",  // Emerald
    "#8B5CF6",  // Violet
    "#F59E0B"   // Amber
  ],
  "background": "#FFFFFF",
  "foreground": "#111827",
  "tableAccent": "#92003A",
  "good": "#10B981",
  "bad": "#EF4444",
  "neutral": "#92003A"
}
```

## Application Rules for This Dashboard

### Page Backgrounds
- All pages: `background: "#FFFFFF"` (white canvas)
- Card/visual containers: white background with subtle border

### KPI Card Styling (per `powerbi-design-layout-themes`)
- **Container background**: `ColorId: 0` (theme background = white)
- **Title text**: `ColorId: 1` (theme foreground = dark slate #111827)
- **Callout values**: 
  - Music: `#92003A` (Dark Wine)
  - Beauty: `#F62477` (Bright Magenta)
  - Gaming: `#3B82F6` (Blue)
  - Tech: `#8B5CF6` (Violet)
  - News: `#10B981` (Emerald)
  - Entertainment: `#F59E0B` (Amber)
- **Rounded corners**: `radius: "15D"` on all visual containers

### Chart Series Colors (ThemeDataColor mapping)
- `ThemeDataColor: 0` → `#92003A` (Dark Wine) — Primary category
- `ThemeDataColor: 1` → `#F62477` (Bright Magenta) — Secondary
- `ThemeDataColor: 2` → `#FFADEE` (Pastel Pink) — Tertiary
- `ThemeDataColor: 3` → `#FFE185` (Soft Sand) — Quaternary
- `ThemeDataColor: 4` → `#3B82F6` (Blue) — Tech/Science
- `ThemeDataColor: 5` → `#10B981` (Emerald) — Success/Good
- `ThemeDataColor: 6` → `#8B5CF6` (Violet) — Gaming
- `ThemeDataColor: 7` → `#F59E0B` (Amber) — Warning/Entertainment

### Slicer Styling
- Background: white (`ColorId: 0`)
- Text: dark slate (`ColorId: 1`)
- Selected item highlight: Magenta (`#F62477`)
- Orientation: Horizontal (`orientation: "1"`), Responsive: false
- Minimum height: 100px

### Visual Container Objects (apply to ALL visuals via theme visualStyles)
```json
"visualContainerObjects": {
  "background": [{ "show": true, "transparency": 0, "color": { "solid": { "color": { "themeColor": "background" } } } }],
  "border": [{ "show": true, "width": 1, "color": { "solid": { "color": { "themeColor": "foregroundNeutralSecondary" } } }, "radius": { "expr": { "Literal": { "Value": "15D" } } }]
}
```

## Complete Theme JSON Location
When applying: overwrite `Youtube.Report/StaticResources/SharedResources/BaseThemes/CY26SU05.json`

**Always delete `cache.abf` before reopening in PBID.**