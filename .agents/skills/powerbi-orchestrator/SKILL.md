---
name: powerbi-orchestrator
description: >
  MASTER SKILL — Single entry point for creating Power BI dashboards from CSV/Excel.
  Interactive workflow with ABSOLUTE guardrails. Loads sub-skills automatically.
  Works with any model. Enforces verification at every step.
tags: [powerbi, master, orchestrator, dashboard, interactive, guardrails, pbip]
load_skills:
  - powerbi-pbir-editor
  - powerbi-tmdl-modeling
  - powerbi-design-layout-themes
  - powerbi-pbir-visuals-specs
  - powerbi-pbir-troubleshooting
  - powerbi-dashboard-from-scratch
---

# 🎯 Power BI Orchestrator — Master Skill

**⚠️ THIS IS THE ONLY POWER BI SKILL YOU SHOULD LOAD.** It automatically loads and coordinates all sub-skills.

**⚠️ FOLLOW EVERY STEP IN ORDER. DO NOT SKIP STEPS. DO NOT REORDER THEM.**

**⚠️ WHEN THE SKILL SAYS "ASK USER":** you MUST ask the user using `clarify()` or in text. Do not assume. Do not guess. Do not use default values without asking.

---

## 🚨 PREFLIGHT: 6 ABSOLUTE GUARDRAILS

Read these NOW. Violating any of them will break the dashboard.

```
┌────────────────────────────────────────────────────────────────────┐
│  🛑 RULE #1: NEVER create model.bim/TMDL from scratch             │
│  User MUST load data in PBID and save as PBIP.                    │
│  No loaded data → ASK USER to load it first.                      │
├────────────────────────────────────────────────────────────────────┤
│  🛑 RULE #2: ALWAYS close PBID before editing files               │
│  Run: taskkill /IM PBIDesktop.exe /F                              │
│  PBID overwrites any changes if it's open.                        │
├────────────────────────────────────────────────────────────────────┤
│  🛑 RULE #3: NEVER create visual.json manually                    │
│  ALWAYS use: pbir add visual <type>                               │
│  Manual visuals cause NullReferenceException.                     │
├────────────────────────────────────────────────────────────────────┤
│  🛑 RULE #4: TMDL requires LF (\\n), NOT CRLF (\\r\\n)            │
│  Python: open(..., newline='\\n')                                  │
│  CRLF → InvalidLineType: Other on EVERY line.                     │
├────────────────────────────────────────────────────────────────────┤
│  🛑 RULE #5: Delete cache.abf before reopening PBID               │
│  rm -f <Project>.SemanticModel/.pbi/cache.abf                     │
│  If not deleted: theme changes will NOT apply.                    │
├────────────────────────────────────────────────────────────────────┤
│  🛑 RULE #6: Do NOT use % in DAX measure names                    │
│  Use "Pct" instead of "%".                                        │
│  % → grouped charts render as empty rectangles.                   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📋 COMPLETE WORKFLOW (8 PHASES)

Use the `todo` tool to track progress. Mark each step `completed` when done AND verified.

---

### PHASE 0: INITIAL INTERACTIVE DECISIONS

**ASK USER (mandatory — do NOT skip this):**

> "To get started, I need to know:
>
> 1. **What's the data file?** (path to .csv or .xlsx)
> 2. **What's the dashboard purpose?** (e.g. sales analysis, performance, inventory, etc.)
> 3. **Who's the audience?** (e.g. executives, operations team, external client)
> 4. **Do you prefer dark mode or light mode?** (if unsure, I'll recommend based on the data)
> 5. **Do you want me to analyze the data and recommend visuals, or do you have a clear idea?"

  Wait for COMPLETE response before continuing.

---

### PHASE 1: PROJECT PREPARATION

**CHECKLIST:**

- [ ] `⏳` ASK USER: "Have you already loaded the data in Power BI Desktop and saved as PBIP?"
  - If NO → give exact instructions:
    1. Open Power BI Desktop (Blank Report)
    2. Get Data → CSV/Excel → select file
    3. Load (or Close & Apply if Transform Data was used)
    4. File → Save As → Power BI Project (*.pbip) → choose folder
    5. **Close Power BI Desktop**
    6. Tell me "done" or "listo"
  - Wait for user confirmation before continuing

- [ ] `⏳` Verify project structure

```bash
ls -R "<Project Path>"
```

Must contain:
  - `<Project>.pbip`
  - `<Project>.Report/definition.pbir`
  - `<Project>.Report/definition/report.json`
  - `<Project>.Report/definition/version.json`
  - `<Project>.Report/definition/pages/pages.json`
  - `<Project>.Report/definition/pages/<page-guid>/page.json`
  - `<Project>.SemanticModel/definition.pbism`
  - `<Project>.SemanticModel/definition/tables/*.tmdl`

  If any file is missing:
  - **ASK USER**: "Missing file(s): [list]. Was the project saved correctly as PBIP? Do you want me to try rebuilding it?"

- [ ] `⏳` Ensure PBID is CLOSED

```bash
taskkill /IM PBIDesktop.exe /F 2>/dev/null; echo "PBID closed"
```

- [ ] `⏳` Verify `pbir` CLI is available

```bash
which pbir || pip install pbir-cli
```

  - If install fails → ASK USER: "Could not install pbir-cli. Can you install it manually with `pip install pbir-cli`?"

- [ ] `⏳` Run structural validation

```bash
python <path-to-skill>/scripts/validate_pbip.py "<Project>.pbip"
```

  - Parse the JSON output
  - If `status === "error"`: report each error to user and ask how to proceed
  - If `status === "ok"` or `"warning"`: continue

---

### PHASE 2: DATA ANALYSIS

- [ ] `⏳` Read table TMDL files to understand available columns

```bash
cat "<Project>.SemanticModel/definition/tables/*.tmdl"
```

  Extract: table names, column names, data types

- [ ] `⏳` If PBID is running, run sample DAX query:

```python
# Use mcp__powerbi_local__list_instances first
# If instance exists, use mcp__powerbi_local__execute_dax
# DAX: EVALUATE TOPN(10, 'table_name')
```

- [ ] `⏳` ASK USER (mandatory — based on real data):

> "I've analyzed the data. The model contains these tables/columns:
> ```
> [list tables and columns with types]
> ```
>
> **My analysis recommendation:**
> Based on the data, I suggest focusing on:
> - [Recommendation 1 with justification]
> - [Recommendation 2 with justification]
> - [Recommendation 3 with justification]
>
> **Does this approach work for you? Or would you prefer a different focus?**

---

### PHASE 3: VISUAL DESIGN DECISIONS

- [ ] `⏳` ASK USER (mandatory — do NOT use defaults without asking):

> "For the visual design, I need your input:
>
> **1. Color theme:** Based on [dashboard purpose], I recommend:
>    - If financial/business data → dark mode (Slate & Terracotta)
>    - If marketing/social media data → light mode (Magenta Blossom)
>    - If environmental/nature data → light mode (Ecotone Spring)
>    - If you want something balanced → dark mode (Roasted Espresso)
>    - If formal/elegant → light mode (Vintage Nordic)
>
> **2. Page layout:** Do you prefer:
>    - Single page with KPIs + charts (compact)
>    - Multiple pages separated by topic (detailed)
>
> **3. Any specific color or branding preferences?**

  Wait for decision. If user is unsure, YOU recommend based on the data.

- [ ] `⏳` Based on user decisions, determine:
  - Theme file to use (see Phase 6)
  - Number of pages
  - Which KPIs go where

---

### PHASE 4: DAX MEASURES

- [ ] `⏳` Determine needed measures (based on agreed analysis from Phase 2)

```python
# Common measures by analysis type — adapt to actual data
suggested_measures = {
    "sales": ["Total Sales", "Average Sale", "Total Quantity", "Avg Ticket"],
    "performance": ["Efficiency Pct", "Completion Pct", "Avg Time"],
    "inventory": ["Total Stock", "Turnover", "Days Without Stock"],
    # etc.
}
```

- [ ] `⏳` ASK USER:

> "For the [purpose] analysis, I propose creating these DAX measures:
>
> ```
> 1. [Measure 1] = [DAX expression] — for [purpose]
> 2. [Measure 2] = [DAX expression] — for [purpose]
> 3. [Measure 3] = [DAX expression] — for [purpose]
> [...]
> ```
>
> **Do you agree? Want to add, modify, or remove any?**

- [ ] `⏳` Inject measures into TMDL (one by one)

```python
# Use mcp__powerbi_local__add_measure_to_tmdl for each measure
# OR patch the TMDL file directly

# CRITICAL:
# ✅ Use "Pct" NOT "%" in names
# ✅ formatString in double quotes: "\"$#,##0\""
# ✅ file encoding: newline='\\n'
# ✅ Do NOT modify partition blocks or annotation PBI_ResultType
```

- [ ] `⏳` Run `fix_tmdl.py` on the SemanticModel to catch any formatting issues

```bash
python <skill-path>/scripts/fix_tmdl.py "<Project>.SemanticModel/definition/"
```

  - If fixes were applied, report them
  - Parse JSON output for verification

- [ ] `⏳` VERIFY: Read the modified TMDL and confirm measures are correct

```bash
grep -A3 "measure '" "<table>.tmdl"
```

---

### PHASE 5: VISUALS

- [ ] `⏳` ASK USER:

> "For the [purpose] dashboard, I propose these visualizations:
>
> **Page 1 — [Page Name]**
> - 🏷️ KPI: [key metric 1]
> - 🏷️ KPI: [key metric 2]
> - 🏷️ KPI: [key metric 3]
> - 🍩 Donut: [category vs measure]
> - 📊 Bar: [category vs measure]
> - 📈 Line: [trend/time series]
> - 🎚️ Slicer: [category filter]
>
> **Does this layout work for you, or would you like changes?**

- [ ] `⏳` For each visual:

1. Connect pbir to project:

```bash
cd "<Project Path>"
pbir connect "<Project>.Report"
pbir ls  # list pages
```

2. Create each visual with `pbir add visual`:

```bash
PAGE="<Project>.Report/<PageGUID>.Page"

# KPIs (card)
pbir add visual card "$PAGE" -n "vis_kpi_1" -t "🔑 Total Sales" -x 20 -y 20 -w 195 -h 105 -d "Values:table.Total Sales"

# Donut chart
pbir add visual donutChart "$PAGE" -n "vis_donut_1" -t "🍩 Sales by Category" -x 20 -y 140 -w 300 -h 280 -d "Category:table.category" -d "Y:table.Total Sales"

# Bar chart
pbir add visual barChart "$PAGE" -n "vis_bar_1" -t "📊 Top Products" -x 340 -y 140 -w 300 -h 280 -d "Category:table.product" -d "Y:table.Total Sales"

# Slicer (CRITICAL: use Values role for pbir-cli)
pbir add visual slicer "$PAGE" -n "vis_slicer_1" -t "" -x 20 -y 435 -w 250 -h 85 -d "Values:table.category"

# Line chart (uses Y, NOT Values!)
pbir add visual lineChart "$PAGE" -n "vis_line_1" -t "📈 Trend" -x 20 -y 535 -w 620 -h 390 -d "Category:table.date" -d "Y:table.Total Sales"
```

3. **CRITICAL:** Check for pre-existing visuals that might conflict

- [ ] `⏳` VERIFY each visual:

```bash
# List created visuals
ls -la "<Project>.Report/definition/pages/<page-guid>/visuals/"
# Each visual must have its own folder with visual.json inside
```

---

### PHASE 6: THEME & STYLING

- [ ] `⏳` Ensure PBID is closed:

```bash
taskkill /IM PBIDesktop.exe /F 2>/dev/null
```

- [ ] `⏳` Delete cache:

```bash
rm -f "<Project>.SemanticModel/.pbi/cache.abf"
```

- [ ] `⏳` Overwrite theme according to Phase 3 decision:

```python
# NEVER create new theme file — ALWAYS overwrite existing
# Find: <Project>.Report/StaticResources/SharedResources/BaseThemes/CY26SU05.json
```

**Pre-built themes (copy based on user's choice):**

**Dark Mode — "Slate & Terracotta" (recommended for financial/business data):**
```json
{
  "name": "CY26SU05",
  "dataColors": ["#A56F63", "#D99B7F", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6"],
  "background": "#0F3040",
  "foreground": "#F8FAFC",
  "tableAccent": "#A56F63",
  "good": "#10B981",
  "bad": "#EF4444",
  "neutral": "#A56F63"
}
```

**Light Mode — "Magenta Blossom" (recommended for marketing/social media):**
```json
{
  "name": "CY26SU05",
  "dataColors": ["#92003A", "#F62477", "#FFADEE", "#FFE185", "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"],
  "background": "#FFFFFF",
  "foreground": "#111827",
  "tableAccent": "#92003A",
  "good": "#10B981",
  "bad": "#EF4444",
  "neutral": "#92003A"
}
```

**Light Mode — "Ecotone Spring" (environmental/nature data):**
```json
{
  "name": "CY26SU05",
  "dataColors": ["#769826", "#A1CB35", "#FFDE4E", "#FF9D4D", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6"],
  "background": "#F5F2EB",
  "foreground": "#1a1a2e",
  "tableAccent": "#769826",
  "good": "#A1CB35",
  "bad": "#EF4444",
  "neutral": "#769826"
}
```

**Dark Mode — "Roasted Espresso" (balanced):**
```json
{
  "name": "CY26SU05",
  "dataColors": ["#60241E", "#95271D", "#B34A44", "#E77B49", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"],
  "background": "#1A0F0D",
  "foreground": "#F8FAFC",
  "tableAccent": "#B34A44",
  "good": "#10B981",
  "bad": "#EF4444",
  "neutral": "#B34A44"
}
```

**Light Mode — "Vintage Nordic" (formal/elegant):**
```json
{
  "name": "CY26SU05",
  "dataColors": ["#0B1849", "#124D1C", "#E4B028", "#EBEDE3", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6"],
  "background": "#EBEDE3",
  "foreground": "#0B1849",
  "tableAccent": "#0B1849",
  "good": "#124D1C",
  "bad": "#C0392B",
  "neutral": "#0B1849"
}
```

- [ ] `⦸` Apply background to each page:

```python
# Read each page.json and add/update objects.background
# ⚠️ CRITICAL: page.json background does NOT accept "show" property
# Only color + transparency
```

- [ ] `⏳` Apply series colors to each visual (dataPoint):

```python
# For each visual.json in pages/*/visuals/*/visual.json:
# - treemap → DO NOT TOUCH (uses dataColors from theme automatically)
# - card → only visualContainerObjects (background, title, border)
# - donut/bar/line → add dataPoint with ThemeDataColor by index
# - slicer → configure orientation, responsive, colors
```

- [ ] `⏳` Apply rounded corners (radius) on each visual:

```python
# In visual.json → visual → visualContainerObjects → border → radius
# ⚠️ CRITICAL: value must have "D" suffix: "15D" not "15"
```

- [ ] `⏳` VERIFY:
  - `cache.abf` was deleted
  - Theme was overwritten (not created as new)
  - page.json files have updated background
  - visual.json files have visualContainerObjects

---

### PHASE 7: COMPLETE VERIFICATION

- [ ] `⏳` Run structural validation:

```bash
python <skill-path>/scripts/validate_pbip.py "<Project>.pbip"
```

  - Parse JSON output
  - ALL checks should pass (or be warnings only)
  - Report any errors to user

- [ ] `⏳` Run TMDL fix (catch any remaining issues):

```bash
python <skill-path>/scripts/fix_tmdl.py "<Project>.SemanticModel/definition/"
```

- [ ] `⏳` Verify no CRLF in TMDL files:

```bash
# Search for CRLF
grep -rl $'\r' "<Project>.SemanticModel/definition/" --include="*.tmdl" 2>/dev/null
# If anything found → run fix_tmdl.py again
```

- [ ] `⏳` Double-check cache.abf was deleted:

```bash
ls "<Project>.SemanticModel/.pbi/cache.abf" 2>/dev/null && echo "⚠️ cache.abf STILL EXISTS" || echo "✅ cache.abf deleted"
```

- [ ] `⏳` Verify UTF-8 without BOM:

```bash
# Check no JSON has BOM
find "<Project Dir>" -name "*.json" -exec file {} \; | grep "BOM" && echo "⚠️ BOM detected" || echo "✅ No BOM"
```

- [ ] `⏳` List complete file structure for user reference:

```bash
find "<Project Dir>" -type f | sort
```

- [ ] `⏳` ASK USER:

> "✅ Structural verification passed. The project is ready to open in Power BI Desktop.
>
> **To test:**
> 1. Open Power BI Desktop
> 2. File → Open → select `<Project>.pbip`
> 3. Wait for all visuals to load
> 4. If you see any error, tell me the exact error message
> 5. If everything looks good, confirm it
>
> **Shall we proceed?**

---

### PHASE 8: POST-DELIVERY (optional)

- [ ] `⏳` If user reports errors → diagnose using `powerbi-pbir-troubleshooting`
- [ ] `⏳` If user wants changes → use `pbir add visual` to add/remove visuals
- [ ] `⏳` If everything is good → ASK USER: "Would you like me to save this configuration as a skill for future similar dashboards?"
- [ ] `⏳` ASK USER: "Are there any new pitfalls or errors you encountered that I should document for next time?"

---

## 📐 PROJECT FILE STRUCTURE REFERENCE

*(Consolidated from powerbi-pbir-editor, powerbi-pbip-bootstrap, and powerbi-dashboard-from-scratch)*

```
YourProject/
├── YourProject.pbip ← ItemShortcut (JSON, schema 1.0.0)
│   {
│     "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
│     "version": "1.0",
│     "artifacts": [{"report": {"path": "YourProject.Report"}}]
│   }
├── .pbi/
│   └── localSettings.json
├── YourProject.Report/
│   ├── definition.pbir ← ReportDefinition (schema 2.0.0)
│   │— DO NOT place inside definition/ — it's a sibling of definition/
│   └── definition/
│       ├── version.json
│       ├── report.json (PBIR, schema 1.0.0, has $schema, themeCollection, pages[])
│       └── pages/
│           ├── pages.json (with pageOrder["guid1", ...])
│           └── {guid}/
│               └── page.json
│               └── visuals/
│                   └── {visual-name}/
│                       └── visual.json
└── YourProject.SemanticModel/
    ├── definition.pbism ← DatasetDefinition (schema 1.0.0)
    └── definition/
        ├── model.tmdl OR tables/*.tmdl
        └── .pbi/
            └── cache.abf ← DELETE before reopening PBID
```

**CRITICAL FOLDER RULE:**
- `definition.pbir` is a SIBLING of `definition/`, not inside it
- Page folders must be named with 20-char lowercase hex GUIDs
- Visuals go in `visuals/{visual-name}/visual.json` — NEVER in page root

---

## 🔧 COMMON PROBLEMS

If you encounter errors, consult `powerbi-pbir-troubleshooting`.

| Error | Most Likely Cause | Immediate Action |
|-------|------------------|------------------|
| `NullReferenceException: GetEnhancedReportDocument` | visual.json created manually | Delete visual and recreate with `pbir add visual` |
| `InvalidLineType: Other` on TMDL line 1 | CRLF in TMDL | Convert to LF: `fix_tmdl.py` |
| `Unsupported db compat level` | compatibilityLevel > 1600 | Change to 1600 |
| Visuals not rendering (empty rectangle) | Direct column in Y/Values of grouped chart | Create DAX measure, use `"Measure"` projection |
| Theme not applying | cache.abf not deleted | Delete and reopen |
| `'show' additional property` error | `show` in page.json background | Remove `show`, keep only color + transparency |
| Slicer not showing items | wrong orientation or responsive=true | orientation="1" + responsive=false + height ≥ 85px |
| `name` property missing | visual.json missing `name` at root | Add `"name": "vis_name"` to JSON root |

---

## 📚 RELATED SKILLS (loaded automatically)

| Skill | Purpose | When to use |
|-------|---------|-------------|
| `powerbi-pbir-editor` | Edit PBIR report structure | Phase 5 (visuals) |
| `powerbi-tmdl-modeling` | DAX measures and TMDL | Phase 4 (measures) |
| `powerbi-design-layout-themes` | Grid, layout, premium themes | Phase 3 and 6 (design + theme) |
| `powerbi-pbir-visuals-specs` | Visual types, roles, projections | Phase 5 (creating visuals) |
| `powerbi-pbir-troubleshooting` | Debugging and error correction | Phase 7 and 8 (verification) |
| `powerbi-dashboard-from-scratch` | Full reference workflow | Phase 1-8 (supplement) |

---

## ✅ SUCCESS CRITERIA

The dashboard is complete when:

- [ ] All phases 0-7 are marked `completed` in your todo checklist
- [ ] No structural validation errors
- [ ] No CRLF in TMDL files
- [ ] `cache.abf` was deleted
- [ ] User confirmed the dashboard opens correctly
- [ ] Visualizations render with data (not empty rectangles)
- [ ] Theme and colors match the user's decision from Phase 3
