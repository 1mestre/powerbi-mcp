---
name: powerbi-orchestrator
description: >-
  MASTER SKILL — Single entry point for creating Power BI dashboards from CSV/Excel.
  Mandatory for any Power BI task, dashboard creation, PBIP generation, DAX modeling,
  or visual report editing. Automatically loads sub-skills and enforces 6 guardrails,
  5 Anti-Gravity pillars, and script verification.
tags: [powerbi, master, orchestrator, dashboard, interactive, guardrails, pbip]
load_skills:
  - powerbi-tmdl-modeling
  - powerbi-design-layout-themes
  - powerbi-pbir-visuals-specs
  - powerbi-pbir-troubleshooting
  - powerbi-html-visuals
  - powerbi-visual-styling
  - powerbi-csv-audit
---

# 🎯 Power BI Orchestrator — Master Skill Hub

**⚠️ THIS IS THE ONLY POWER BI SKILL YOU SHOULD LOAD.** It automatically loads and coordinates all sub-skills.

---

## 🛠️ MCP TOOLS INTEGRATION (`powerbi-local` SERVER)

When Power BI Desktop is running locally, the agent MUST leverage the 5 MCP tools from `server.py`:

| Action | MCP Tool | Execution Context |
|---|---|---|
| 1. Scan Ports | `list_instances()` | Discover active SSAS engine port. |
| 2. Fetch Schema | `get_schema(port)` | Retrieve tables, columns, data types, and existing measures. |
| 3. Query Data | `execute_dax(port, query)` | Run `EVALUATE` queries to inspect sample rows and statistics live. |
| 4. Inject DAX Measure | `add_measure_to_tmdl(tmdl_path, name, expression, format_string)` | Append DAX measures safely into TMDL without touching partitions. |
| 5. Generate HTML Visual | `generate_html_visual(...)` | Execute DAX, generate self-contained HTML visual, write measure to TMDL. |

---

## 🚨 PREFLIGHT: 6 ABSOLUTE GUARDRAILS

```text
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
│  🛑 RULE #4: TMDL requires LF (\n), NOT CRLF (\r\n)               │
│  Python: open(..., newline='\n')                                  │
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

## ⚡ 5 PILARES ANTI-GRAVITY (Canónicos)

1. **Custom Visual Binding:** Dual projection `Values` + manifest role (`content` para HTML Content).
2. **Canvas vs Theme:** Set canvas background in `page.json` `objects.background` (never `show` property!).
3. **Color Key Mapping:** Card:`labels`, Donut:`labels`, Bar:`dataPoint`/`labelColor`, Slicer:`items`.
4. **Multi-Color Bars:** `scopeId` Comparison selector in `dataPoint` — `Right` = Literal direct without `expr`.
5. **Grid 1280x720 + Márgenes:** Canvas 1280x720, margins 20px, gaps 20px, min heights (KPI 100px, Chart 260px).

---

## 📋 COMPLETE 8-PHASE WORKFLOW

### PHASE 0: INITIAL INTERACTIVE DECISIONS
**ASK USER (mandatory):**
1. What's the data file path? (.csv or .xlsx)
2. What's the dashboard purpose? (sales analysis, performance, etc.)
3. Who's the audience? (executives, operations, external client)
4. Dark mode or light mode preference? (Default: **Slate & Terracotta** dark mode for business data)
5. Do you want data analysis recommendations or do you have specific visual ideas?

### PHASE 1: PROJECT PREPARATION & MCP SCAN
1. Confirm user loaded data into PBID and saved as `.pbip`.
2. Call `list_instances()` to detect if PBID is open and get port.
3. If PBID is open, call `get_schema(port)` to inspect tables/columns live.
4. Close PBID (`taskkill /IM PBIDesktop.exe /F`) BEFORE file modifications.
5. Run `python scripts/validate_pbip.py "<Project>.pbip"`.

### PHASE 2: DATA ANALYSIS
1. Read `.tmdl` files or use `get_schema()` output.
2. Run sample DAX queries (`execute_dax()`) if PBID is running.
3. Recommend key metrics and dimensions to the user.

### PHASE 3: VISUAL DESIGN DECISIONS
1. Ask user for theme preference (Slate & Terracotta dark mode, Magenta Blossom light mode, Ecotone Spring, Roasted Espresso, Vintage Nordic).
2. Establish layout grid (1280x720) and page structure.

### PHASE 4: DAX MEASURES CREATION
1. Determine needed measures (`Total Sales`, `Avg Discount Pct`, `Title Count`, etc.).
2. Inject measures into TMDL using `add_measure_to_tmdl` or Python (`newline='\n'`).
3. Ensure no `%` symbol in measure names; double-quote format strings (`"$#,##0"`).
4. Run `python scripts/fix_tmdl.py "<Project>.SemanticModel/definition/"`.

### PHASE 5: VISUALS CREATION (`pbir-cli` & HTML Visuals)
1. Run `pbir connect "<Project>.Report"`.
2. For standard visuals, use `pbir add visual <type> "$PAGE" -n "name" -t "Title" -x X -y Y -w W -h H -d "Role:table.field"`.
3. For HTML Content visuals, invoke `generate_html_visual(...)` to build HTML measure in TMDL and bind measure to visual `Values`.
4. Point all chart values (`Y` / `Values`) to DAX measures using `"Measure"` projection type.

### PHASE 6: THEME & STYLING APPLICATION (MANDATORY EXECUTION)
1. Ensure PBID is closed (`taskkill /IM PBIDesktop.exe /F`).
2. Delete `<Project>.SemanticModel/.pbi/cache.abf`.
3. **MANDATORY:** Run `python scripts/apply_theme.py "<Project>.pbip" --theme slate-terracotta` (or chosen theme). This automatically patches `CY26SU05.json`, updates `page.json` backgrounds on all pages, sets visual container backgrounds/borders, and formats typography with high contrast.
4. Verify `page.json` background contains solid theme color (no `show` property!).

### PHASE 7: COMPLETE VERIFICATION (MANDATORY SCRIPT EXECUTION)
1. **MANDATORY:** Run `python scripts/check_overlaps.py "<Project>.Report"` to ensure 0 visual overlaps or canvas width/height boundary violations (x + width <= 1280, y + height <= 720).
2. **MANDATORY:** Run `python scripts/validate_pbip.py "<Project>.pbip"` -> MUST reach 52/54+ OK.
3. Run `python scripts/fix_tmdl.py "<Project>.SemanticModel/definition/"`.
4. Confirm 0 CRLF in TMDL (`grep -rl $'\r'`).
5. Confirm `cache.abf` deleted before reopening PBID.
6. Confirm UTF-8 without BOM across all JSON files.

### PHASE 8: POST-DELIVERY
Ask user to open `.pbip` in Power BI Desktop and confirm clean rendering.

---

## 🔗 SUB-SKILLS REFERENCE
- `powerbi-tmdl-modeling`
- `powerbi-design-layout-themes`
- `powerbi-pbir-visuals-specs`
- `powerbi-pbir-troubleshooting`
- `powerbi-html-visuals`
- `powerbi-visual-styling`
- `powerbi-csv-audit`

