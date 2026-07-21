---
name: pbir-dark-theme-styling
description: Apply dark-theme styling patterns to PBIR visual.json files — container backgrounds, borders, axis colors, legend text, card labels, slicer items, title fontColor, and dataPoint Percent tuning.
---

# PBIR Dark Theme Visual Styling

This skill captures the exact JSON patterns for retrofitting PBIR visual containers with dark-theme colors. Use when a report page has a dark canvas (e.g. `#0F3040`) but visuals lack card backgrounds, have invisible axis labels, or use tinted bar colors.

## Color Palette Reference (Slate & Terracotta, CY26SU05)

| Token | Hex | Purpose |
|-------|-----|---------|
| `page-bg` | `#0F3040` | Page canvas (darkest) |
| `card-bg` | `#1A4055` | Visual container background (one step lighter) |
| `foreground` | `#F8FAFC` | All text/labels (near-white) |
| `border` | `#285468` | Subtle container border |
| `gridline` | `#4B5563` | Muted axis gridlines |
| `data[0..7]` | `#A56F63`, `#D99B7F`, `#3B82F6`, `#10B981`, `#F59E0B`, `#8B5CF6`, `#EC4899`, `#14B8A6` | 8 theme data colors |

## Patterns

### 1. Opaque Card Background

Set every visual's background to `card-bg` with explicit opaque transparency. This creates visible card separation against the page:

```json
"background": [
  {
    "properties": {
      "show": { "expr": { "Literal": { "Value": "true" } } },
      "color": {
        "solid": {
          "color": { "expr": { "Literal": { "Value": "'#1A4055'" } } }
        }
      },
      "transparency": { "expr": { "Literal": { "Value": "0D" } } }
    }
  }
]
```

> `transparency: 0D` = fully opaque. The `D` suffix (decimal double) is required by PBIR schema.

### 2. Container Border

```json
"border": [
  {
    "properties": {
      "show": { "expr": { "Literal": { "Value": "true" } } },
      "color": {
        "solid": {
          "color": { "expr": { "Literal": { "Value": "'#285468'" } } }
        }
      },
      "radius": { "expr": { "Literal": { "Value": "8D" } } }
    }
  }
]
```

### 3. Chart Axis Colors (barChart, columnChart, lineChart, areaChart)

Add both `categoryAxis` and `valueAxis` with explicit label and gridline colors:

```json
"objects": {
  "categoryAxis": [{
    "properties": {
      "labelColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } } } },
      "gridlineColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#4B5563'" } } } } }
    }
  }],
  "valueAxis": [{
    "properties": {
      "labelColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } } } },
      "gridlineColor": { "solid": { "color": { "expr": { "Literal": { "Value": "'#4B5563'" } } } } }
    }
  }]
}
```

### 4. Title fontColor

Always add explicit `fontColor` in `visualContainerObjects.title`:

```json
"title": [{
  "properties": {
    "show": { "expr": { "Literal": { "Value": "true" } } },
    "text": { "expr": { "Literal": { "Value": "'My Title'" } } },
    "fontColor": {
      "solid": {
        "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } }
      }
    }
  }
}]
```

### 5. Donut/Pie Legend fontColor

Legend labels on dark backgrounds need explicit text color:

```json
"legend": [{
  "properties": {
    "show": { "expr": { "Literal": { "Value": "true" } } },
    "text": {
      "fontColor": {
        "solid": {
          "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } }
        }
      }
    }
  }
}]
```

### 6. KPI Card Callout Value

Card visuals use `objects.labels` (NOT `dataLabels`):

```json
"labels": [{
  "properties": {
    "color": {
      "solid": {
        "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } }
      }
    },
    "fontSize": { "expr": { "Literal": { "Value": "28D" } } }
  }
}]
```

### 7. Slicer Item Colors

```json
"items": [{
  "properties": {
    "fontColor": {
      "solid": {
        "color": { "expr": { "Literal": { "Value": "'#F8FAFC'" } } }
      }
    },
    "background": {
      "solid": {
        "color": { "expr": { "Literal": { "Value": "'#1A4055'" } } }
      }
    }
  }
}]
```

### 8. Bar Chart Top-N Colors — dataPoint Percent Nuance

For top-N charts where you cycle through `dataPoint[]` entries with `ThemeDataColor` (no scopeId/Comparison selectors), the `Percent` field controls the tint:

| Percent | Visual Effect |
|---------|--------------|
| `0` | Full-strength theme color |
| `20` | Lighter tint (20% toward white) |
| `-20` | Darker shade (20% toward black) |
| `-100` | Pure black |

To have all bars at full strength, set `Percent: 0` on every entry. For 10 bars with only 8 theme palette colors, cycle ColorId 0–7 then 0–1:

```json
"dataPoint": [
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 1, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 2, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 3, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 4, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 5, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 6, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 7, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } } } },
  { "properties": { "fill": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 1, "Percent": 0 } } } } } } }
]
```

### 9. Visual-Type Styling Checklist

When applying dark-theme styling to a PBIR report, verify each visual:

| Visual Type | Must Check |
|-------------|------------|
| **All** | background (card-bg, not page-bg), `show: true`, `transparency: 0D`, border + radius, title fontColor |
| **barChart / columnChart** | categoryAxis (labelColor + gridlineColor), valueAxis (labelColor + gridlineColor), dataPoint colors |
| **donutChart / pieChart** | legend fontColor, dataPoint colors |
| **card** | labels color, categoryLabel hide or transparent |
| **slicer** | items fontColor + background, general responsive + orientation |
| **lineChart / areaChart** | categoryAxis (labelColor + gridlineColor), valueAxis (labelColor + gridlineColor), legend fontColor |

## Python Bulk Update Template

```python
import json, os, glob

FOREGROUND = "#F8FAFC"
GRIDLINE = "#4B5563"
CARD_BG = "#1A4055"
BORDER_COLOR = "#285468"

visuals_dir = r"path/to/Report/definition/pages/*/visuals/*/visual.json"

for vpath in glob.glob(visuals_dir, recursive=True):
    with open(vpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    visual = data.get("visual", data)
    vco = visual.setdefault("visualContainerObjects", {})
    
    # Background — opaque card bg
    bg = vco.setdefault("background", [{"properties": {}}])
    props = bg[0].setdefault("properties", {})
    props["show"] = {"expr": {"Literal": {"Value": "true"}}}
    props["color"] = {"solid": {"color": {"expr": {"Literal": {"Value": f"'{CARD_BG}'"}}}}}
    props["transparency"] = {"expr": {"Literal": {"Value": "0D"}}}
    
    # Border
    border = vco.setdefault("border", [{"properties": {}}])
    props = border[0].setdefault("properties", {})
    props["show"] = {"expr": {"Literal": {"Value": "true"}}}
    props["color"] = {"solid": {"color": {"expr": {"Literal": {"Value": f"'{BORDER_COLOR}'"}}}}}
    props["radius"] = {"expr": {"Literal": {"Value": "8D"}}}
    
    # Title fontColor
    for title_entry in vco.get("title", []):
        title_entry.setdefault("properties", {})["fontColor"] = \
            {"solid": {"color": {"expr": {"Literal": {"Value": f"'{FOREGROUND}'"}}}}}
    
    # Type-specific objects
    vtype = visual.get("visualType", "")
    objs = visual.setdefault("objects", {})
    
    if vtype in ("barChart", "columnChart", "lineChart", "areaChart"):
        objs["categoryAxis"] = [{"properties": {
            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{FOREGROUND}'"}}}}},
            "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{GRIDLINE}'"}}}}}
        }}]
        objs["valueAxis"] = [{"properties": {
            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{FOREGROUND}'"}}}}},
            "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{GRIDLINE}'"}}}}}
        }}]
    
    elif vtype in ("donutChart", "pieChart"):
        objs["legend"] = [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{FOREGROUND}'"}}}}}}
        }}]
    
    elif vtype == "card":
        objs["labels"] = [{"properties": {
            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{FOREGROUND}'"}}}}},
            "fontSize": {"expr": {"Literal": {"Value": "28D"}}}
        }}]
    
    elif vtype == "slicer":
        objs["items"] = [{"properties": {
            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{FOREGROUND}'"}}}}},
            "background": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{CARD_BG}'"}}}}}
        }}]
    
    with open(vpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

## Key Pitfalls

- **`show` is valid in `visualContainerObjects.background`** (visual.json) but **INVALID in `page.json → objects.background`** — that only accepts `color` + `transparency`.
- **`transparency` requires the `D` suffix** (e.g. `"0D"`, `"100D"`) — raw integers like `"0"` may be silently ignored.
- **Card visuals** use `objects.labels` for the callout value, NOT `objects.dataLabels`. The latter controls something else.
- **Slicers without `general.responsive: false`** will ignore `orientation` and collapse into a vertical list when container height is small.
- **`dataPoint` without `selector`** applies colors in order — if the number of categories exceeds the number of entries, excess categories revert to automatic cycling.
