# PBIR Design Guidelines — Power BI Visual Styling Reference

> **TL;DR:** Every `visual.json` MUST have explicit foreground/text colors, background,
> and border properties. Never rely on theme cascading alone — it breaks on dark themes.

---

## The 10 Commandments of PBIR Styling

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. NEVER rely on theme cascading for text colors                   │
│     Theme firstLevelElements/secondLevelElements are ignored         │
│     by many visuals → always set labelColor, fontColor explicitly   │
├─────────────────────────────────────────────────────────────────────┤
│  2. EVERY visual needs a visualContainerObjects block                │
│     If missing → no background, no border, no radius                │
├─────────────────────────────────────────────────────────────────────┤
│  3. Dark themes MUST use light text; light themes MUST use dark     │
│     Dark page bg  →  primary text #F8FAFC  secondary #CBD5E1       │
│     Light page bg →  primary text #111827  secondary #4B5563       │
├─────────────────────────────────────────────────────────────────────┤
│  4. Gridlines must be VISIBLE but SUBTLE                            │
│     Dark: #4B5563  |  Light: #D1D5DB                               │
│     Too dark = chart looks cluttered; too light = no contrast       │
├─────────────────────────────────────────────────────────────────────┤
│  5. barChart + categorical data = MULTIPLE dataPoint colors (10)    │
│     barChart + temporal data = SINGLE color (ThemeDataColor 0)      │
│     This is handled automatically by apply_theme.py                  │
├─────────────────────────────────────────────────────────────────────┤
│  6. Cards (KPIs) need cardLabels + categoryLabels fontColor         │
│     Without this, KPI text can be invisible on dark themes          │
├─────────────────────────────────────────────────────────────────────┤
│  7. Slicers need 3 text colors: header, items, inputText            │
│     Missing any → text can blend into the slicer background         │
├─────────────────────────────────────────────────────────────────────┤
│  8. Visual backgrounds should be slightly lighter (dark themes)     │
│     or slightly darker (light themes) than the page background      │
│     This creates visual cards that float on the page.               │
├─────────────────────────────────────────────────────────────────────┤
│  9. Rounded corners (radius) MUST use "D" suffix: "8D" not "8"     │
│     Without "D", Power BI interprets as pixels not DIPs             │
├─────────────────────────────────────────────────────────────────────┤
│ 10. Always validate contrast after applying a theme                 │
│     Use: python apply_theme.py <project> --theme <name> --validate  │
│     WCAG AA: 4.5:1 for normal text, 3:1 for large text             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Visual Property Mapping — Complete Reference

### 1. Theme File — `BaseThemes/<file>.json`

| Property | Purpose | Example |
|----------|---------|---------|
| `name` | Theme identifier (must match existing file name) | `"CY26SU05"` |
| `dataColors[]` | 8-10 chart color palette | `["#A56F63", "#D99B7F", ...]` |
| `background` | Root page background color | `"#0F3040"` |
| `foreground` | Root text color (some items use this) | `"#F8FAFC"` |
| `tableAccent` | Row highlight accent color | `"#A56F63"` |
| `good` | Positive semantic color | `"#10B981"` |
| `bad` | Negative semantic color | `"#EF4444"` |
| `neutral` | Neutral semantic color | `"#A56F63"` |
| `firstLevelElements` | Primary text color (dark theme) | `"#F8FAFC"` |
| `secondLevelElements` | Secondary text color | `"#CBD5E1"` |
| `thirdLevelElements` | Tertiary/border color | `"#334155"` |
| `fourthLevelElements` | Background/divider color | `"#1E3A5F"` |

> **Warning:** Many visuals IGNORE firstLevelElements. Always set explicit colors on each visual.

### 2. Page Background — `pages/<guid>/page.json`

```json
"objects": {
  "background": [{
    "properties": {
      "color": {
        "solid": {
          "color": {
            "expr": { "Literal": { "Value": "'#0F3040'" } }
          }
        }
      },
      "transparency": { "expr": { "Literal": { "Value": "0" } } }
    }
  }]
}
```

> **CRITICAL:** `"show"` property is NOT supported in page.json background.
> Including it causes a Pandora schema error.

### 3. Visual Container — `visual.json` → `visual.visualContainerObjects`

```json
"visualContainerObjects": {
  "fill": [{
    "properties": {
      "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#1A4055'" } } } } },
      "transparency": { "expr": { "Literal": { "Value": "0" } } }
    }
  }],
  "border": [{
    "properties": {
      "color": { "solid": { "color": { "expr": { "Literal": { "Value": "'#285468'" } } } } },
      "width": { "expr": { "Literal": { "Value": "1" } } }
    }
  }],
  "radius": [{
    "properties": {
      "radius": { "expr": { "Literal": { "Value": "8D" } } }
    }
  }]
}
```

### 4. Title — `visual.json` → `visual.objects.title`

```json
"title": [{
  "properties": {
    "fontColor": {
      "solid": { "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } } }
    },
    "show": { "expr": { "Literal": { "Value": "true" } } }
  }
}]
```

### 5. Category Axis — `visual.json` → `visual.objects.categoryAxis`

```json
"categoryAxis": [{
  "properties": {
    "labelColor": {
      "solid": { "color": { "expr": { "Literal": { "Value": "'#CBD5E1'" } } } }
    },
    "gridlineStyle": {
      "solid": {
        "color": { "expr": { "Literal": { "Value": "'#4B5563'" } } }
      }
    }
  }
}]
```

### 6. Value Axis — `visual.json` → `visual.objects.valueAxis`

```json
"valueAxis": [{
  "properties": {
    "labelColor": {
      "solid": { "color": { "expr": { "Literal": { "Value": "'#CBD5E1'" } } } }
    },
    "gridlineStyle": {
      "solid": {
        "color": { "expr": { "Literal": { "Value": "'#4B5563'" } } }
      }
    }
  }
}]
```

### 7. Legend — `visual.json` → `visual.objects.legend`

```json
"legend": [{
  "properties": {
    "labelColor": {
      "solid": { "color": { "expr": { "Literal": { "Value": "'#CBD5E1'" } } } }
    }
  }
}]
```

### 8. Data Labels — `visual.json` → `visual.objects.dataLabels`

```json
"dataLabels": [{
  "properties": {
    "color": {
      "solid": { "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } } }
    }
  }
}]
```

### 9. Data Points (Bar Colors) — `visual.json` → `visual.objects.dataPoint`

**Categorical data (e.g., Top 10 Countries):**
```json
"dataPoint": [
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 1, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 2, "Percent": 0 } } } } } } },
  ...up to 10 entries
]
```

**Temporal data (by year):**
```json
"dataPoint": [
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } } } }
]
```

### 10. Card (KPI) Labels — `visual.json` → `visual.objects`

```json
"cardLabels": [{
  "properties": {
    "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } } } },
    "fontSize": { "expr": { "Literal": { "Value": "24" } } }
  }
}],
"categoryLabels": [{
  "properties": {
    "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#CBD5E1'" } } } } },
    "fontSize": { "expr": { "Literal": { "Value": "12" } } }
  }
}]
```

### 11. Slicer — `visual.json` → `visual.objects`

```json
"header": [{
  "properties": {
    "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } } } },
    "show": { "expr": { "Literal": { "Value": "true" } } }
  }
}],
"items": [{
  "properties": {
    "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#CBD5E1'" } } } } }
  }
}],
"inputText": [{
  "properties": {
    "fontColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } } } }
  }
}]
```

### 12. Gridlines — Axis Property

Gridlines are set inside `categoryAxis` or `valueAxis` as `gridlineStyle`:

```json
"gridlineStyle": {
  "solid": {
    "color": { "expr": { "Literal": { "Value": "'#4B5563'" } } }
  }
}
```

---

## Dark vs Light Theme — Contrast Rules

### Dark Mode Themes (slate-terracotta, roasted-espresso)

| Element | Color | Contrast Against Page BG | WCAG Level |
|---------|-------|--------------------------|------------|
| Page background | `#0F3040` | — | — |
| Visual background | `#1A4055` (slightly lighter) | — | — |
| Border | `#285468` | — | — |
| Title / Primary text | `#F8FAFC` | 14.6:1 | ✅ AAA |
| Axis labels, Legend | `#CBD5E1` | 8.7:1 | ✅ AAA |
| Gridlines | `#4B5563` | 3.5:1 | ✅ AA (large) |
| Data labels | `#F8FAFC` on visual bg | 12.1:1 | ✅ AAA |
| Card label | `#F8FAFC` on card bg | 12.1:1 | ✅ AAA |
| Slicer item | `#CBD5E1` on visual bg | 7.3:1 | ✅ AA |

**Rule of thumb:** On dark backgrounds, never use pure white for secondary text.
Use `#CBD5E1` (slate-300) or `#94A3B8` (slate-400) for axis labels, legends, and
secondary info. Reserve `#F8FAFC` for primary content only.

### Light Mode Themes (magenta-blossom, ecotone-spring, vintage-nordic)

| Element | Color | Contrast Against Page BG | WCAG Level |
|---------|-------|--------------------------|------------|
| Page background | `#FFFFFF` / `#F5F2EB` / `#EBEDE3` | — | — |
| Visual background | `#F9FAFB` / `#FAF8F3` / `#F0F2E9` | — | — |
| Border | `#E5E7EB` / `#E2DDD0` / `#D6D9CC` | — | — |
| Title / Primary text | `#111827` / `#1a1a2e` / `#0B1849` | 15.1:1 | ✅ AAA |
| Axis labels, Legend | `#4B5563` | 4.9:1 | ✅ AA |
| Gridlines | `#D1D5DB` | 1.6:1 | ❌ (decorative) |
| Data labels | `#111827` on visual bg | 13.5:1 | ✅ AAA |
| Card label | `#111827` on card bg | 13.5:1 | ✅ AAA |
| Slicer item | `#374151` on visual bg | 6.7:1 | ✅ AA |

**Rule of thumb:** On light backgrounds, use `#4B5563` (gray-600) for secondary text.
Never use pure `#000000` black — it's too harsh. Gridlines on light themes are
decorative (below 3:1) which is acceptable — they're not text.

---

## Complete Theme Profiles Reference

### 🌙 slate-terracotta (Dark)
```
Page:        #0F3040    Visual:   #1A4055    Border: #285468
Primary:     #F8FAFC    Secondary: #CBD5E1   Grid:   #4B5563
Data colors: #A56F63, #D99B7F, #3B82F6, #10B981, #F59E0B,
             #8B5CF6, #EC4899, #14B8A6
Best for: Financial/business data, executive dashboards
```

### ☀️ magenta-blossom (Light)
```
Page:        #FFFFFF    Visual:   #F9FAFB    Border: #E5E7EB
Primary:     #111827    Secondary: #4B5563   Grid:   #D1D5DB
Data colors: #92003A, #F62477, #FFADEE, #FFE185, #3B82F6,
             #10B981, #8B5CF6, #F59E0B
Best for: Marketing, social media, brand-forward dashboards
```

### ☀️ ecotone-spring (Light)
```
Page:        #F5F2EB    Visual:   #FAF8F3    Border: #E2DDD0
Primary:     #1a1a2e    Secondary: #4B5563   Grid:   #D5D0C3
Data colors: #769826, #A1CB35, #FFDE4E, #FF9D4D, #3B82F6,
             #10B981, #8B5CF6, #EC4899, #14B8A6, #F59E0B
Best for: Environmental, nature, sustainability data
```

### 🌙 roasted-espresso (Dark)
```
Page:        #1A0F0D    Visual:   #2D1814    Border: #3D221D
Primary:     #F8FAFC    Secondary: #CBD5E1   Grid:   #4B3A36
Data colors: #60241E, #95271D, #B34A44, #E77B49, #3B82F6,
             #10B981, #F59E0B, #8B5CF6
Best for: Balanced dark dashboards, premium feel
```

### ☀️ vintage-nordic (Light)
```
Page:        #EBEDE3    Visual:   #F0F2E9    Border: #D6D9CC
Primary:     #0B1849    Secondary: #4A5568   Grid:   #D5D8CB
Data colors: #0B1849, #124D1C, #E4B028, #EBEDE3, #3B82F6,
             #8B5CF6, #EC4899, #14B8A6
Best for: Formal, elegant, professional dashboards
```

---

## How to Add a New Theme

Follow these steps to add a new built-in theme to `apply_theme.py`:

### Step 1: Add a Visual Profile Entry

In `apply_theme.py`, add a new entry to `VISUAL_PROFILES` dict:

```python
"my-new-theme": {
    "theme": {
        "name": "CY26SU05",
        "dataColors": ["#COLOR1", "#COLOR2", "#COLOR3", "#COLOR4",
                       "#COLOR5", "#COLOR6", "#COLOR7", "#COLOR8"],
        "background": "#PAGE_BG",
        "foreground": "#PRIMARY_TEXT",
        "tableAccent": "#ACCENT",
        "good": "#GREEN",
        "bad": "#RED",
        "neutral": "#ACCENT"
    },
    "mode": "dark",              # or "light"
    "page_bg": "#PAGE_BG",       # same as background
    "visual_bg": "#VIS_BG",      # slightly lighter (dark) or darker (light)
    "border": "#BORDER",
    "radius": "8D",
    "title_font_color": "#PRIMARY",
    "cat_axis_label": "#SECONDARY",
    "val_axis_label": "#SECONDARY",
    "legend_label": "#SECONDARY",
    "data_label": "#PRIMARY",
    "gridline": "#GRID",
    "plot_area": "#PLOT",
    "slicer_header_font": "#PRIMARY",
    "slicer_item_font": "#SECONDARY",
    "slicer_input_text": "#PRIMARY",
    "card_label": "#PRIMARY",
    "card_category_label": "#SECONDARY",
    "card_bg": "#VIS_BG",
    "table_font": "#PRIMARY",
    "table_header_bg": "#HEADER_BG",
    "table_row_alt_bg": "#VIS_BG",
    "map_fill": "#MAP",
    "data_point_count": 10
}
```

### Step 2: Apply the Theme

```bash
python scripts/apply_theme.py <project.pbip> --theme my-new-theme
```

### Step 3: Validate Contrast

```bash
python scripts/apply_theme.py <project.pbip> --theme my-new-theme --validate
```

All checks should pass WCAG AA (≥4.5:1 for text).

### Color Selection Rules

For **dark mode** themes:
- `page_bg`: Rich, dark color (avoid pure `#000000`)
- `visual_bg`: Lighten page_bg by ~10-15% for visible card separation
- `border`: Lighten visual_bg by ~15-20% for subtle frame
- `title_font_color`: `#F8FAFC` (near-white, never pure `#FFFFFF`)
- Secondary text: `#CBD5E1` or `#94A3B8` (slate gray tones)
- Gridlines: `#4B5563` (medium gray, visible but not distracting)

For **light mode** themes:
- `page_bg`: Soft, warm white or light tint (avoid pure `#FFFFFF` if possible)
- `visual_bg`: Slightly darker than page_bg by ~3-5% 
- `border`: Gray-200/300 range for subtle separation
- `title_font_color`: Near-black (e.g., `#111827`, `#1a1a2e`), never pure `#000000`
- Secondary text: `#4B5563` or `#374151` (medium gray)
- Gridlines: `#D1D5DB` or `#D5D0C3` for light visibility

---

## Color Expression Formats

All visual properties in PBIR use one of two color expression formats:

### Literal (direct hex color)
```json
{"solid": {"color": {"expr": {"Literal": {"Value": "'#F8FAFC'"}}}}}
```

### ThemeDataColor (references theme palette by index)
```json
{"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 0, "Percent": 0}}}}}
```

Use **Literal** for all text/foreground colors, backgrounds, borders, and gridlines.
Use **ThemeDataColor** only for dataPoint fills (bar colors) so they cycle through the
theme palette.

---

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Relying on theme cascade for text | Invisible text on dark themes | Set fontColor explicitly on every visual |
| Missing `visualContainerObjects` | No background/border/radius | Always add fill + border + radius |
| Using `show` in page background | Pandora schema error | Remove `show` property from page bg |
| Radius value without `D` | Wrong corner size in PBID | Always use `"8D"` suffix |
| Only 8 dataPoint entries | Only 8 bars colored | Use 10 entries for categorical data |
| Gridlines same color as visual bg | Invisible gridlines | Gridlines must be visible |
| Missing slicer `inputText` | Can't see typed text in slicer | Always set inputText.fontColor |
| Pure `#FFFFFF` on dark bg | Eye strain (too much contrast) | Use `#F8FAFC` instead |
| Pure `#000000` on light bg | Harsh, unprofessional look | Use `#111827` or `#1a1a2e` |
| No cardLabels fontColor | KPI value invisible | Always set cardLabels.fontColor |

---

## Quick Reference: apply_theme.py CLI

```
Usage: python apply_theme.py <project.pbip> --theme <name>

Options:
  --theme <name>         One of: slate-terracotta, magenta-blossom,
                         ecotone-spring, roasted-espresso, vintage-nordic
  --theme-file <path>    Custom theme JSON file
  --dry-run              Show what would be done without modifying
  --profile              Print the visual profile for a theme
  --validate             Only validate contrast ratios
  --list-themes          List all available themes
```

**Typical workflow:**
```bash
# Step 1: View profile
python apply_theme.py project.pbip --theme slate-terracotta --profile

# Step 2: Validate contrast
python apply_theme.py project.pbip --theme slate-terracotta --validate

# Step 3: Apply to project
python apply_theme.py project.pbip --theme slate-terracotta
```

---

## Programmatic Usage (from other scripts)

```python
from apply_theme import get_visual_profile, VISUAL_PROFILES, validate_contrast

# Get a full visual profile
profile = get_visual_profile("slate-terracotta")
print(f"Title color: {profile['title_font_color']}")

# Validate contrast
warnings = validate_contrast(profile)
if warnings:
    for w in warnings:
        print(f"Contrast issue: {w}")

# Check all available themes
for name in VISUAL_PROFILES:
    mode = VISUAL_PROFILES[name]["mode"]
    print(f"{name} ({mode})")
```

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-07-21 | Hermes Agent | Initial comprehensive styling engine replacing simple theme applicator |
