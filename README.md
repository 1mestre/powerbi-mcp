# ⚡ Power BI Hermes Framework — Multi-Agent PBIP & PBIR Executive Dashboard Engine

[![Power BI PBIR](https://img.shields.io/badge/Power_BI-PBIP%20%7C%20PBIR%202.0-yellow?style=for-the-badge&logo=powerbi)](https://powerbi.microsoft.com/)
[![Framework Version](https://img.shields.io/badge/Framework-2.0.0--Gold-blue?style=for-the-badge)](https://github.com/1mestre/desktop-ssas-mcp)
[![Harness Compatibility](https://img.shields.io/badge/Agents-Hermes%20%7C%20Anti--Gravity%20%7C%20Claude%20%7C%20Cursor-green?style=for-the-badge)](https://github.com/1mestre/desktop-ssas-mcp)

The **Power BI Hermes Framework** is a complete, multi-agent engineering framework designed to give AI assistants (**Hermes, Anti-Gravity, Claude Code, Cursor, Windsurf, Cline**) the exact skills, script engines, visual design math, and verification guardrails needed to build **deterministic, high-contrast, executive-ready Power BI Projects (`.pbip`)** in a single pass — eliminating infinite correction loops, unstyled default light themes, layout overlaps, and broken TMDL files.

---

## 🌟 What Makes This Framework Unique?

Unlike generic scripts or simple MCP wrappers, this framework combines:
1. **Master Orchestrator & 7 Specialized Skills** (`.agents/skills/`) for multi-page layout, TMDL measure injection, WCAG contrast styling, and visual specification locks.
2. **Deterministic Python Verification Engine** (`framework/scripts/`) that programmatically patches themes, updates canvas backgrounds, validates contrast, checks coordinate overlaps per page, and fixes line endings.
3. **5 Anti-Gravity Pillars & 6 Absolute Guardrails** that enforce strict grid math (5 KPIs max per row, `w=232px`, `gap=20px`), schema version locks (`2.9.0`), and explicit color key mappings.
4. **Desktop SSAS MCP Server Integration** (`server.py` via `launch.py` using `powerbi-local`) for live DAX query execution, port discovery, and TMDL schema inspection directly against running Power BI Desktop instances on Windows.

---

## ⚡ Quick Start & Universal Agent Activation

### 🤖 Option A: Direct Prompt for Any AI Agent (Hermes, Anti-Gravity, Claude, Cursor)

Copy and paste this prompt into a new chat with your AI agent:

```text
Task: Initialize Power BI Hermes Framework for Dashboard Development.

1. Repository setup: Clone or pull https://github.com/1mestre/desktop-ssas-mcp.git
2. Environment: Create virtual environment (.venv) and install requirements:
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
3. Skill Activation:
   - If using Hermes: Load skill 'powerbi-orchestrator' (auto-loads all sub-skills).
   - If using Anti-Gravity / Claude Code / Cursor: Copy .agents/skills/* into your agent's active skills path and read .agents/skills/powerbi-orchestrator/SKILL.md.
4. Mandatory Execution Rules:
   - Phase 6: ALWAYS run: python framework/scripts/apply_theme.py "<Project>.pbip" --theme slate-terracotta
   - Phase 7: ALWAYS run: python framework/scripts/check_overlaps.py "<Project>.Report"
5. Confirm framework readiness to start building the dashboard.
```

---

### 🔧 Option B: Manual Installation & Integration

#### 1. Install Skills into Hermes
```powershell
# Copy framework skills to Hermes active profile path
xcopy /E /I /Y .agents\skills\* %LOCALAPPDATA%\hermes\skills\
```

#### 2. Install Skills into Workspace (Anti-Gravity / Claude Code / Cursor / Windsurf)
```powershell
# Copy framework skills to current project workspace
xcopy /E /I /Y .agents\skills\* .agents\skills\
```

#### 3. Register MCP Server (Optional — for Live SSAS DAX Execution & Port Scanning)

Add the `powerbi-local` server to your agent's MCP configuration file:

##### Hermes (`config.yaml`)
```yaml
mcp_servers:
  powerbi-local:
    command: C:/path/to/desktop-ssas-mcp/.venv/Scripts/python.exe
    args:
      - C:/path/to/desktop-ssas-mcp/launch.py
    connect_timeout: 30
    timeout: 120
```

##### Cursor / Cline / Windsurf (`mcp.json` / `claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "powerbi-local": {
      "command": "C:\\path\\to\\desktop-ssas-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\desktop-ssas-mcp\\launch.py"
      ]
    }
  }
}
```

---

## 📁 Framework Architecture & File Map

```text
desktop-ssas-mcp/
├── README.md                           # Master documentation & installation guide
├── requirements.txt                    # Core Python dependencies (fastmcp, pythonnet, etc.)
├── launch.py                           # Sanitizing launcher wrapper (prevents PYTHONPATH collisions)
├── server.py                           # MCP server tools (list_instances, get_schema, execute_dax, add_measure_to_tmdl, generate_html_visual)
├── pbi_connector.py                    # ADOMD.NET connector & active SSAS port scanner
├── html_generators.py                  # HTML visual generators (bar, donut, KPI, column, line, table)
├── fix_tmdl_format.py                  # TMDL formatString sanitizer
├── new_powerbi_dashboard.py            # Automation suite for batch generation
├── framework/                          # 📦 Core Framework Distribution
│   ├── SKILL.md                        # Framework Master Entry Point
│   ├── DESIGN_GUIDELINES.md            # Visual aesthetics, WCAG contrast & theme tokens
│   ├── references/
│   │   └── guardrails.md               # 6 non-negotiable pre-flight guardrails
│   └── scripts/                        # 🛠️ Deterministic Python Execution Engine
│       ├── apply_theme.py              # Visual styling & theme engine (Dark/Light mode)
│       ├── check_overlaps.py           # Per-page visual overlap & 1280x720 boundary checker
│       ├── validate_pbip.py            # 54-check PBIP structural validator
│       ├── fix_tmdl.py                 # TMDL CRLF→LF, BOM & syntax sanitizer
│       ├── audit_csv.py                # Pre-flight CSV auditor (BOM, quotes, delimiters)
│       └── csv_fix.py                  # Programmatic CSV cleaner
└── .agents/
    └── skills/                         # 🤖 AI Agent Skill Suite (Hermes, Anti-Gravity, Claude, Cursor)
        ├── powerbi-orchestrator/       # MASTER SKILL (Loads all sub-skills automatically)
        ├── powerbi-tmdl-modeling/      # DAX measures, TMDL formatting & partition preservation
        ├── powerbi-design-layout-themes/ # 1280x720 Grid math, 5 themes & WCAG 2.1 AA rules
        ├── powerbi-pbir-visuals-specs/  # Visual types, queryState projections & 2.9.0 schema lock
        ├── powerbi-pbir-troubleshooting/ # 5 Anti-Gravity Pillars & operational trap fixes
        ├── powerbi-visual-styling/      # Visual-type specific text & container background rules
        ├── powerbi-csv-audit/           # Pre-flight CSV data pipeline audit
        └── pbir-dark-theme-styling/     # Dark theme JSON exact property templates
```

---

## 🎯 Guided 8-Phase Workflow

Every agent executing tasks with this framework MUST follow this 8-phase workflow:

| Phase | Name | What Happens | Mandatory Tool / Script Gate |
|:---:|---|---|---|
| **0** | **Interactive Discovery** | Ask user for data path, dashboard purpose, audience, and theme preference. | `audit_csv.py` (if input is CSV) |
| **1** | **Environment Check** | Verify PBIP directory structure and ensure Power BI Desktop is closed. | `validate_pbip.py` |
| **2** | **Data Analysis** | Inspect semantic model schema and sample rows. | `get_schema()` / `execute_dax()` via MCP |
| **3** | **Visual Design** | Select one of 5 premium themes and establish page grid. | `powerbi-design-layout-themes` |
| **4** | **DAX Modeling** | Inject DAX measures into `.tmdl` files (`newline='\n'`). | `fix_tmdl.py` |
| **5** | **Visual Creation** | Generate visuals using `pbir add visual <type>` (never manual JSON). | `pbir-cli` |
| **6** | **Theme & Styling** | **MANDATORY EXECUTION:** Apply theme and patch `page.json` backgrounds. | `python scripts/apply_theme.py "<Project>.pbip" --theme slate-terracotta` |
| **7** | **Final Verification** | **MANDATORY EXECUTION:** Verify 0 overlaps and 52/54+ PBIP checks. | `python scripts/check_overlaps.py` & `validate_pbip.py` |
| **8** | **Human Delivery** | Delete `cache.abf` and ask user to open `.pbip` in Power BI Desktop. | — |

---

## 🛡️ 6 Absolute Guardrails & ⚡ 5 Anti-Gravity Pillars

### 🛑 6 Absolute Guardrails (Violations = Broken Dashboard)
1. **REGLA #1: NEVER create `model.bim` / TMDL from scratch.** The user MUST load data into Power BI Desktop and save as `.pbip`.
2. **REGLA #2: ALWAYS close Power BI Desktop before editing files.** Run `taskkill /IM PBIDesktop.exe /F`.
3. **REGLA #3: NEVER create `visual.json` manually.** ALWAYS use `pbir add visual <type>`.
4. **REGLA #4: TMDL requires strictly LF line endings (`\n`), NOT CRLF (`\r\n`).** Python files MUST use `open(..., newline='\n')`.
5. **REGLA #5: ALWAYS delete `cache.abf` before reopening Power BI Desktop.** (`<Project>.SemanticModel/.pbi/cache.abf`).
6. **REGLA #6: NEVER use `%` in DAX measure names.** Use `Pct` instead (`Avg Discount Pct`).

---

### ⚡ 5 Anti-Gravity Pillars (Deterministic Layout & Contrast)

| Pilar | Core Rule | Implementation Detail |
|---|---|---|
| **1. Custom Visual Binding** | Dual projection in `queryState` | Duplicate field projections under both `"Values"` AND manifest role (`"content"` for HTML Content). |
| **2. Canvas Background** | Direct `page.json` override | Edit `objects.background` in `page.json` directly. **NO `show` property in `page.json` background** (causes schema error). |
| **3. Color Key Mapping** | Strict keys per visual type | Card:`labels`/`categoryLabels`, Donut:`labels`/`legend`, Bar:`dataPoint`/`labelColor`, Slicer:`items`/`header`. |
| **4. Multi-Color Bars** | `scopeId` selectors in `dataPoint` | Inject `scopeId` Comparison array per category value. `Comparison.Right` contains `Literal` directly without `expr`. |
| **5. Grid Math & Page Limits** | 1280x720 grid & visual limits | **Max 5-6 visuals per page.** **Max 5 KPIs per row** (`w=232px`, `gap=20px`, `margin=20px`). Formula: `x_i = 20 + i * 252`. |

---

## 🎨 5 Premium Themes Catalogue

`apply_theme.py` includes 5 complete built-in visual profiles for dark and light modes:

| Theme Name | Mode | Palette Overview | Recommended Usage |
|---|:---:|---|---|
| **`slate-terracotta`** | Dark | Canvas `#0F3040`, Cards `#1A4055`, Text `#F8FAFC`, Accents `#A56F63`, `#D99B7F` | **Executive / Financial (Default)** |
| **`magenta-blossom`** | Light | Canvas `#FFFFFF`, Cards `#F9FAFB`, Text `#111827`, Accents `#92003A`, `#F62477` | Marketing & Social Media |
| **`ecotone-spring`** | Light | Canvas `#F5F2EB`, Cards `#FAF8F3`, Text `#1A1A2E`, Accents `#769826`, `#A1CB35` | Environment & Sustainability |
| **`roasted-espresso`** | Dark | Canvas `#1A0F0D`, Cards `#2D1814`, Text `#F8FAFC`, Accents `#60241E`, `#E77B49` | Premium Operations & Retail |
| **`vintage-nordic`** | Light | Canvas `#EBEDE3`, Cards `#F0F2E9`, Text `#0B1849`, Accents `#0B1849`, `#124D1C` | Corporate & Formal Reporting |

---

## 🛠️ Verification Script Engine Reference

### 1. `apply_theme.py` (Theme Application & Visual Styling Engine)
Applies complete visual styling to all `page.json` files, `CY26SU05.json`, and `visual.json` containers:
```powershell
python framework/scripts/apply_theme.py "F:/projects/Sales.pbip" --theme slate-terracotta
```

### 2. `check_overlaps.py` (Visual Layout & Boundary Checker)
Checks every page for visual collisions, boundary overflow (`x+w > 1280` or `y+h > 720`), and page overcrowding (>6 visuals):
```powershell
python framework/scripts/check_overlaps.py "F:/projects/Sales.pbip"
```

### 3. `validate_pbip.py` (54-Check PBIP Validator)
Runs full structural analysis across `.pbip`, `.pbir`, `pages.json`, `visual.json`, and `.tmdl` files:
```powershell
python framework/scripts/validate_pbip.py "F:/projects/Sales.pbip"
```

### 4. `fix_tmdl.py` (TMDL Line Ending & BOM Sanitizer)
Enforces LF line endings (`\n`), removes UTF-8 BOM, and quotes unquoted `formatString` entries in TMDL files:
```powershell
python framework/scripts/fix_tmdl.py "F:/projects/Sales.SemanticModel/definition/"
```

### 5. `audit_csv.py` (Pre-flight CSV Auditor)
Audits raw input CSV files for unbalanced quotes, inconsistent column counts, UTF-8 BOM, and CRLF:
```powershell
python framework/scripts/audit_csv.py "data/sales_raw.csv"
```

---

## 🔌 Desktop SSAS MCP Server Tools API (`powerbi-local`)

When running Power BI Desktop on Windows, the MCP server (`server.py`) exposes these 5 native tools:

| Tool | Purpose | Output Format |
|---|---|---|
| **`list_instances()`** | Auto-scans local AppData to detect active Power BI Desktop SSAS ports. | `[{"path": "...", "port": "54321"}]` |
| **`get_schema(port)`** | Retrieves full semantic model schema (tables, columns, data types, measures). | `[{"Name": "Sales", "Columns": [...]}]` |
| **`execute_dax(port, query)`** | Executes live DAX `EVALUATE` queries against the active SSAS engine. | `[{"Sales[Country]": "Mexico", "Total": 125000}]` |
| **`add_measure_to_tmdl(tmdl_path, name, expression, format_string)`** | Appends DAX measures safely into `.tmdl` files before partition blocks. | Success / error string |
| **`generate_html_visual(...)`** | Generates self-contained HTML visual measures for Daniel Marsh-Patrick's *HTML Content* visual. | `{"html": "...", "tmdl_result": "..."}` |

---

## 🔗 Credits & References

- [Skill Creator Guidelines](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) — Anthropic
- [Power-BI-Visuals-Using-Claude-AI-HTML-DAX](https://github.com/Fasaclox/Power-BI-Visuals-Using-Claude-AI-HTML-DAX) — Fasaclox
- [HTML Content Visual](https://appsource.microsoft.com/en-us/product/power-bi-visuals/WA104380985) — Daniel Marsh-Patrick
- [Model Context Protocol](https://modelcontextprotocol.io) — Anthropic
