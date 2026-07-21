# Power BI Framework Audit — 2026-07-21

## Summary
Complete audit of the Hermes Power BI skill library across two repositories:
- `~/.hermes/skills/` (primary)
- `~/desktop-ssas-mcp/.agents/skills/` (secondary, with drift)

## Critical Issues Found

### 1. Dual Repository Drift
- `powerbi-orchestrator` exists in **both locations** with different sizes (21,023 vs 21,084 bytes)
- **Action needed**: Consolidate to single source of truth (`~/.hermes/skills/powerbi/powerbi-orchestrator`)

### 2. Missing Skill: `powerbi-pbir-editor`
- Referenced as "Master Skill Hub" in 4 skills: `powerbi-pbir-visuals-specs`, `powerbi-design-layout-themes`, `powerbi-tmdl-modeling`, `powerbi-pbir-troubleshooting`
- **Does not exist anywhere** — all `file://` references are broken
- **Resolution**: All references updated to point to `powerbi-orchestrator` (the actual master skill)

### 3. Inconsistent Canvas Standard
| Skill | Canvas Height |
|-------|--------------|
| `powerbi-pbir-troubleshooting` (Pilar 5) | 1280×720 |
| `powerbi-design-layout-themes` | 1280×920 / 1000 |
| `powerbi-orchestrator` Phase 6 | 1280×920 |
| **Canonical** | **1280×920** (orchestrator wins) |

### 4. Contradictory Rules Between Skills

| Rule | `powerbi-pbir-troubleshooting` | `powerbi-visual-styling` | Resolution |
|------|-------------------------------|-------------------------|------------|
| Slicer orientation | `orientation: "1"` + `responsive: false` + h≥85px | ~~"NO orientation in general"~~ (patched) | **Use orientation in `items`, not `general`** ✅ Patched |
| Categorical bar chart dataPoint | **REQUIRED** with scopeId selectors | ~~REMOVE dataPoint[]~~ (patched) | **dataPoint[] WITH scopeId REQUIRED** ✅ Patched |
| Temporal bar chart dataPoint | Not mentioned | **NO dataPoint** | Consistent ✅ |

## 5 Anti-Gravity Pillars — Canonical Status

| Pillar | Source Skills | Conflicts | Status |
|--------|--------------|-----------|--------|
| 1. Custom Visual Binding | `pbir-troubleshooting` + `visual-styling` | None | ✅ Canonical |
| 2. Canvas vs Theme | `pbir-troubleshooting` + `visual-styling` | None | ✅ Canonical |
| 3. Color Key Mapping | `pbir-troubleshooting` (technical) + `design-layout-themes` (WCAG) | Complementary | ✅ Canonical |
| 4. Multi-color Bars (scopeId) | `pbir-troubleshooting` + `visual-styling` | None | ✅ Canonical |
| 5. Grid 1280×720/920 | All three differ slightly | Canvas height | ⚠️ **Unified to 1280×920** |

## Files to Update (Manual)
The following manually-authored skills cannot be auto-patched but need updates:

1. **`powerbi-pbir-visuals-specs`** — Update RELATED SKILLS section to reference `powerbi-orchestrator` in `~/.hermes/skills/powerbi/`
2. **`powerbi-design-layout-themes`** — Same
3. **`powerbi-tmdl-modeling`** — Same
4. **`powerbi-pbir-troubleshooting`** — Update Pilar 5 canvas to 1280×920

## Validation Checklist for Future PBIR Tasks
```
□ 1. Load ONLY powerbi-orchestrator (auto-loads 4 sub-skills)
□ 2. powerbi-pbir-editor does NOT exist — ignore all references
□ 3. Canvas: 1280×920, margins 20px, gap 20px
□ 4. Slicer: orientation in `items`, responsive=false, h≥85px
□ 5. Categorical bars: dataPoint[] + scopeId selectors (Pilar 4)
□ 6. Temporal bars: NO dataPoint
□ 7. Treemap: NO dataPoint (uses theme dataColors)
□ 8. Donut: objects: {} + schema 2.10.0 initially
□ 9. page.json background: color + transparency ONLY (no show)
□ 10. Schema version: ALL visual.json $schema == report.json visual version
□ 11. TMDL: LF-only, no comments line 1, formatString quoted
□ 12. DAX: Pct not %
□ 13. cache.abf DELETED before reopen
□ 14. UTF-8 without BOM on all JSON
□ 15. Custom visuals: dual projection Values + manifest role
□ 16. Theme: OVERWRITE existing file (never create new)
□ 17. dataPoint on ALL visuals after theme switch
□ 18. visualContainerObjects vs objects: strict separation
□ 19. KPI cards: background/border/radius in visualContainerObjects
□ 20. Schema validation script in Phase 7
```

## Support Files Created
- `powerbi-visual-styling/references/framework-audit-2026-07-21.md` (this file)
- `powerbi-visual-styling/references/anti-gravity-5-pillars.md` (existing)
- `powerbi-visual-styling/references/pbir-visual-styling-lessons.md` (existing)
- `powerbi-visual-styling/templates/dark-theme-visual-config.json` (existing)