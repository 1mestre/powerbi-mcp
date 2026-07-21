# Bar Chart Color Rules in Power BI PBIR

## Categorical Bars (distinct colors per bar)
For charts like "Top 10 Countries" where each bar is a distinct category, use `dataPoint` with cycling `ThemeDataColor`:

```json
"objects": {
  "dataPoint": [
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 0, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 1, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 2, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 3, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 4, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 5, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 6, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 7, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 0, "Percent": 0}}}}}}},
    {"properties": {"fill": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 1, "Percent": 0}}}}}}}
  ]
}
```

Create 8-10 entries cycling ColorId 0-7 (and back). Tested and verified against PBID — `dataPoint` is correct for single-series bar charts with distinct categories. `fillRule` is NOT recommended (renders inconsistently).

## Temporal Bars (single color)
For charts like "Content by Year", use single `defaultColor` or omit dataPoint entirely:

```json
"objects": {
  "defaultColor": [{
    "properties": {
      "fill": {
        "solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 0, "Percent": 0}}}}
      }
    }
  }]
}
```

## What NOT To Do
- `fillRule` instead of `dataPoint` → inconsistent rendering, sometimes all bars same color
- `dataPoint` on temporal data → cycling colors imply distinct series per year
- Remove objects entirely → bars default to first theme color (acceptable for temporal, wrong for categorical)
- Mix `dataPoint` and `fillRule` → conflict, bars may render same color
