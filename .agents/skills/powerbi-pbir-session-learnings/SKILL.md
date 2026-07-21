---
name: powerbi-pbir-session-learnings
description: Session-specific learnings, templates, and references for PBIR CLI dashboard development. Captures patterns from real projects (YouTube, Elanco, etc.) to avoid re-learning pitfalls.
tags: [powerbi, pbir, templates, session-learnings, pbip]
---

# PBIR Session Learnings Skill

This skill captures reusable patterns, templates, and references discovered during actual Power BI dashboard development sessions using the PBIR CLI (`pbir-cli`). It complements the master `powerbi-orchestrator` skill with session-specific artifacts.

## When to Use
- Starting a new PBIP dashboard project
- Need templates for pages, visuals, or measures
- Applying a specific theme (Magenta Blossom, Slate & Terracotta, etc.)
- Debugging TMDL or visual.json issues
- Need reference measures for common patterns (multi-language text search, percentages, etc.)

## Structure

### References (`references/`)
| File | Purpose |
|------|---------|
| `channels_tmdl_measures.tmdl` | Complete TMDL with 18 measures for YouTube channels analysis (multi-language keyword detection, category counts, percentages) |
| `magenta_blossom_theme.md` | Complete theme specification for Magenta Blossom (light mode marketing theme) including color mapping, visual styling rules, and application checklist |

### Templates (`templates/`)
| File | Purpose |
|------|---------|
| `page_template.json` | Minimal page.json scaffold — copy and replace `{{PAGE_GUID}}` and `{{PAGE_DISPLAY_NAME}}` |
| `card_visual_template.json` | Card visual binding template for `pbir add visual --from-json` |
| `donut_visual_template.json` | Donut chart visual binding template |

### Scripts (future)
- `apply_theme.py` — Script to overwrite CY26SU05.json with full theme including visualStyles
- `validate_layout.py` — Check visual overlaps and minimum sizing

## Key Patterns Learned

### 1. Multi-language Keyword Measures
Use `CONTAINSSTRING` with OR chains for each language variant. Column3 (Keywords) is the primary categorization field.

```dax
measure 'Music Channels' = CALCULATE(
  COUNTROWS('channels'),
  CONTAINSSTRING('channels'[Column3], "music") ||
  CONTAINSSTRING('channels'[Column3], "música") ||
  CONTAINSSTRING('channels'[Column3], "müzik") ||
  ...
)
```

### 2. Percentage Measures (Pct not %)
```dax
measure 'Music Pct' = DIVIDE([Music Channels], [Total Channels])
  formatString: "0.00%"
```
**Never use `%` in measure names** — causes empty rectangles in grouped charts.

### 3. Visual Creation via PBIR CLI
```bash
# Card (KPI)
pbir add visual card "Report/Page.Page" -n "vis_name" -t "📊 Title" -x 20 -y 20 -w 280 -h 140 -d "values:Table.Measure"

# Donut Chart
pbir add visual donutChart "Report/Page.Page" -n "vis_name" -t "🍩 Title" -x 20 -y 140 -w 300 -h 300 -d "category:Table.Column" -d "y:Table.Measure"

# Bar Chart
pbir add visual barChart "Report/Page.Page" -n "vis_name" -t "📊 Title" -x 340 -y 140 -w 400 -h 300 -d "category:Table.Column" -d "y:Table.Measure"
```

### 4. Page Creation (manual JSON + pages.json update)
1. Create GUID folder under `definition/pages/`
2. Write `page.json` with schema 2.1.0
3. Add GUID to `pages.json` → `pageOrder` array

### 5. Theme Application Checklist
- [ ] Close PBID: `taskkill /IM PBIDesktop.exe /F`
- [ ] Delete cache: `rm -f Project.SemanticModel/.pbi/cache.abf`
- [ ] Overwrite `CY26SU05.json` with complete theme (dataColors + visualStyles)
- [ ] Update each `page.json` with background object (color + transparency only, NO `show`)
- [ ] Run `validate_pbip.py` and `fix_tmdl.py`

## Related Skills
- `powerbi-orchestrator` — Master workflow (loads this as reference)
- `powerbi-pbir-visuals-specs` — Visual types, roles, projections
- `powerbi-tmdl-modeling` — DAX measure patterns
- `powerbi-design-layout-themes` — Layout grid, WCAG, premium themes
- `powerbi-pbir-troubleshooting` — Error diagnosis

## Session Origin
Created from **YouTube Channels Dashboard** session (43K channels, 21K creators, 3-page Magenta Blossom theme).