# Power BI Desktop Local MCP Server

A **Model Context Protocol (MCP) server** that gives AI assistants (Claude Desktop, Cursor, Cline, Hermes, and others) direct, programmatic access to locally running **Power BI Desktop** instances on Windows.

The agent can discover open reports, inspect the semantic model schema, execute arbitrary DAX queries, write DAX measures permanently to TMDL files, and — new in this version — **generate fully custom HTML visualizations** using live data from the model, ready to drop into Power BI's native *HTML Content* visual.

---

## ⚡ Quick Install Prompt

Copy and paste this into a new session with your AI agent to auto-configure the environment:

```
1. **Dependency Installation:** If the `.venv/` directory does not exist, initialize a Python virtual environment (`python -m venv .venv`), activate it, and install all dependencies declared in `requirements.txt`.
2. **Skill Registration (Hermes):** Load the orchestrator skill:
   `skill_view(name='powerbi-orchestrator')` — this is the single entry point.
   For other agents, copy `.agents/skills/powerbi-orchestrator/` to your skills directory.
3. **MCP Server Registration:** Register the `powerbi-local` MCP server in your global configuration file (e.g., in Hermes: `config.yaml`, in Cursor/Cline: `mcpjson.json`).
   - **CRITICAL:** Configure the command pointing to the Python executable of the local virtual environment (`.venv/Scripts/python.exe`) and the arguments pointing to the `launch.py` script. This prevents sys.path conflicts (PYTHONPATH pollution) when importing the `mcp` library.
4. **Framework Registration:** Copy `framework/` into your agent's workspace or skills directory. This contains 4 validation scripts, the guardrails reference, and the complete orchestrator workflow.
5. **Guided Workflow:** Load the orchestrator skill (`powerbi-orchestrator`) — it automates the 8-phase interactive workflow: ask → analyze → bootstrap → model → design → build → verify → deliver. Run validation scripts between each phase.
6. **Next Steps (Request from Human):** Once installation is complete:
   - "I have successfully installed and configured the Power BI Orchestrator framework."
   - "Please open Power BI Desktop with your project, or provide a CSV/Excel file to start a new dashboard."
```

---

## 🔧 Key Features

| Feature | Description |
|---|---|
| **Dynamic Port Discovery** | Power BI Desktop assigns a random local SSAS port every session. This server auto-scans `AppData` to find and resolve active ports. |
| **ADOMD.NET Connection** | Uses `pythonnet` to load the native `Microsoft.PowerBI.AdomdClient.dll` shipped with Power BI Desktop — no MSOLAP driver conflicts. |
| **Schema Inspection** | Reads full semantic model metadata: tables, columns, data types, visibility. |
| **JSON-Safe DAX Execution** | Runs `EVALUATE SUMMARIZECOLUMNS(...)` and similar, converting .NET decimals, dates, and nulls to clean Python/JSON types. |
| **TMDL Measure Writer** | Writes DAX measures directly to `.tmdl` files so they persist across Power BI sessions. |
| **HTML Visual Generator** | Generates self-contained HTML charts (bar, donut, KPI, clustered bar, stacked column, line, table) from live DAX data — inspired by the [Power-BI-Visuals-Using-Claude-AI-HTML-DAX](https://github.com/Fasaclox/Power-BI-Visuals-Using-Claude-AI-HTML-DAX) project. |
| **Self-Sanitizing Environment** | Clears `PYTHONPATH`/`PYTHONHOME` at startup to prevent host-environment collisions with `pywintypes` or `pythonnet`. |

---

## 📁 Project Structure

```
desktop-ssas-mcp/
├── server.py              # MCP server — tools: list_instances, get_schema, execute_dax, add_measure_to_tmdl, generate_html_visual
├── pbi_connector.py       # ADOMD.NET connector + active port scanner
├── html_generators.py     # HTML visual generators (7 chart types)
├── launch.py              # Sanitizing launcher wrapper
├── create_dashboard.py    # Standalone Plotly dashboard (browser preview)
├── fix_tmdl_format.py     # Utility: fix unquoted formatString values in TMDL
├── new_powerbi_dashboard.py # Full automation: CSV/Excel → finished PBIP (38 functions)
├── test_adomd.py          # Standalone connection test script
├── requirements.txt       # Python dependencies
├── framework/             # 🆕 Power BI Orchestrator framework
│   ├── SKILL.md           # Master orchestrator skill
│   ├── DESIGN_GUIDELINES.md # Visual aesthetic rules & guidelines
│   ├── references/
│   │   └── guardrails.md  # 6 absolute non-negotiable rules
│   └── scripts/
│       ├── validate_pbip.py  # 11-structural-check validator (54 checks)
│       ├── fix_tmdl.py       # CRLF→LF, formatString, BOM fixer
│       ├── apply_theme.py    # 5 premium themes + custom (Dark/Light mode)
│       ├── check_overlaps.py # Visual overlap, boundary & page capacity checker
│       ├── audit_csv.py      # Pre-flight CSV auditor (BOM, quotes, delimiters)
│       └── csv_fix.py         # Programmatic CSV cleaner
├── .agents/
│   └── skills/            # AI agent skills (Hermes, Anti-Gravity, Claude Code, Cursor)
│       ├── powerbi-orchestrator/       # Master entry point (loads sub-skills auto)
│       ├── powerbi-tmdl-modeling/      # DAX measures + TMDL formatting rules
│       ├── powerbi-design-layout-themes/ # 1280x720 Grid math, WCAG contrast, 5 themes
│       ├── powerbi-pbir-visuals-specs/  # Visual types, queryState schemas, 2.9.0 lock
│       ├── powerbi-pbir-troubleshooting/ # 5 Anti-Gravity Pillars & trap fixes
│       ├── powerbi-visual-styling/      # Per-visual-type text & background rules
│       ├── powerbi-csv-audit/           # Standalone CSV audit rules
│       └── pbir-dark-theme-styling/     # Dark theme JSON templates
```

---

## 🎯 Power BI Orchestrator Framework

The **Power BI Orchestrator** is a complete, model-agnostic framework for agent-driven dashboard creation. It wraps the MCP server capabilities into a guardrail-enforced, interactive 8-phase workflow.

### 8-Phase Workflow

| Phase | What Happens | Validation Script |
|-------|-------------|-------------------|
| 0 | **Interactive Discovery** — Ask user about purpose, audience, data source | `audit_csv.py` (if CSV/Excel) |
| 1 | **Environment Check** — Verify MCP, skills, scripts, PBID status | `validate_pbip.py` |
| 2 | **Data Import** — User imports CSV/Excel in PBID, saves as PBIP | — |
| 3 | **Model Analysis** — Agent reads schema, suggests measures | `get_schema()` via MCP |
| 4 | **Measure Injection** — Write DAX to TMDL, fix formatting | `fix_tmdl.py` |
| 5 | **Theme Selection** — Apply one of 5 premium themes | `apply_theme.py` |
| 6 | **Visual Creation** — Prompt user for chart types, create via `pbir add visual` | `check_overlaps.py` |
| 7 | **Final Verification** — Full validation + cache cleanup | `validate_pbip.py` + `check_overlaps.py` |
| 8 | **Human Review** — User opens PBID, confirms rendering | — |

### 🛑 6 Absolute Guardrails

1. **NEVER** create `model.bim` / TMDL from scratch — user must load data in Power BI Desktop first.
2. **ALWAYS** close Power BI Desktop before editing files (`taskkill /IM PBIDesktop.exe /F`).
3. **NEVER** create `visual.json` manually — always use `pbir add visual <type>`.
4. **TMDL requires LF** (`\n`), NOT CRLF (`\r\n`). Always write TMDL in Python with `newline='\n'`.
5. **Delete** `<Project>.SemanticModel/.pbi/cache.abf` before reopening Power BI Desktop.
6. **NEVER** use `%` in DAX measure names — use `Pct` instead (`Avg Discount Pct`).

### ⚡ 5 Anti-Gravity Pillars (Deterministic Styling)

1. **Custom Visual Binding:** Duplicate projections in `queryState` under both `"Values"` and manifest role (`"content"` for HTML Content).
2. **Canvas Background:** Set canvas background in `page.json` `objects.background` (never use `show` property in `page.json` background!).
3. **Strict Color Key Mapping:**
   - `card` KPI: `"labels"` → `"color"`, `"categoryLabels"` → `"show": false`
   - `donutChart`: `"labels"` → `"color"`, `"legend"` → `"labelColor"`
   - `barChart`/`columnChart`: `"dataPoint"` → `"fill"`, `"dataLabels"` → `"labelColor"`, `"categoryAxis"`/`valueAxis` → `"labelColor"`
   - `slicer`: `"items"` → `"fontColor"`, `"header"` → `"show": false`
4. **Multi-Color Bars:** Array of `scopeId` Comparison selectors in `dataPoint` — `Right` = `Literal` direct without outer `expr`.
5. **1280x720 Grid & Capacity Limits:**
   - Canvas 1280x720 (margins 20px, gaps ≥ 20px).
   - Max **5 to 6 visuals per page**.
   - Max **5 KPIs per row** (`w=232px`, `gap=20px`, `margin=20px`). Formula: `x_i = 20 + i * 252`.

### Quick Start (for any AI agent)

```python
# Load the orchestrator
skill_view(name='powerbi-orchestrator')

# Or for non-Hermes agents, copy .agents/skills/powerbi-orchestrator/
# and read the SKILL.md — the agent will follow the 8-phase workflow

# Run validation at any time
python framework/scripts/validate_pbip.py MyProject.pbip
python framework/scripts/fix_tmdl.py MyProject.SemanticModel/
python framework/scripts/apply_theme.py MyProject.pbip --theme slate-terracotta
python framework/scripts/check_overlaps.py MyProject.pbip
```

### For fully automated creation (no interactive prompts):

```bash
python new_powerbi_dashboard.py --create MyDashboard data.csv --theme 3
```

---

## 📋 Prerequisites

1. **OS:** Windows (required for Power BI Desktop and .NET assembly loading)
2. **Python:** 3.10 or higher
3. **Power BI Desktop:** Standard edition (`C:\Program Files\Microsoft Power BI Desktop`) or Microsoft Store edition

---

## 🚀 Installation & Setup

### 1. Clone & Set Up Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Test the Connection

With Power BI Desktop open and a dataset loaded:

```powershell
fastmcp run server.py
```

Or run the standalone test:

```powershell
.\.venv\Scripts\python.exe test_adomd.py
```

### 3. Register the MCP Server in Your AI Client

#### Hermes (`config.yaml`)

```yaml
mcp_servers:
  powerbi-local:
    command: C:/Users/{User}/desktop-ssas-mcp/.venv/Scripts/python.exe
    args:
      - C:/Users/{User}/desktop-ssas-mcp/launch.py
    connect_timeout: 30
    timeout: 120
```

#### Cursor / Cline (`mcpjson.json`)

```json
{
  "mcpServers": {
    "powerbi-local": {
      "command": "C:\\Users\\{User}\\desktop-ssas-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\{User}\\desktop-ssas-mcp\\launch.py"
      ]
    }
  }
}
```

#### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "powerbi-local": {
      "command": "C:\\Users\\{User}\\desktop-ssas-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\{User}\\desktop-ssas-mcp\\launch.py"
      ]
    }
  }
}
```

---

## 🛠 MCP Tools Reference

### `list_instances()`

Scans local AppData for active Power BI Desktop SSAS workspaces.

**Returns:** `[{"path": "...", "port": "12345"}, ...]`

---

### `get_schema(port)`

Retrieves the full semantic model schema from the specified port.

**Args:**
- `port` — from `list_instances()`

**Returns:** `[{"Name": "TableName", "Columns": [{"Name": "col", "DataType": "String", "IsHidden": false}]}, ...]`

---

### `execute_dax(port, query)`

Executes a DAX query and returns clean JSON-serializable results.

**Args:**
- `port` — from `list_instances()`
- `query` — DAX string, e.g. `EVALUATE SUMMARIZECOLUMNS('Sales'[Country], "Total", SUM('Sales'[Amount]))`

**Returns:** `[{"Sales[Country]": "Mexico", "Total": 125000.0}, ...]`

---

### `add_measure_to_tmdl(tmdl_path, name, expression, format_string?)`

Writes a new DAX measure directly to a `.tmdl` semantic model file, inserting it before the `partition` block (or at end of file). Validates for duplicates before writing.

**Args:**
- `tmdl_path` — absolute path to the table `.tmdl` file
- `name` — measure name (e.g. `"Total Sales"`)
- `expression` — DAX formula (e.g. `SUM('Sales'[Amount])`)
- `format_string` *(optional)* — e.g. `"$#,##0"`

**Returns:** Success or error string.

---

### `generate_html_visual(port, query, chart_type, label_key, value_key, ...)`

**The core integration with the [Fasaclox HTML+DAX pattern](https://github.com/Fasaclox/Power-BI-Visuals-Using-Claude-AI-HTML-DAX).**

Executes a DAX query, generates a self-contained HTML visual from the results, and optionally writes it as a DAX measure to a `.tmdl` file. The resulting HTML can be placed in Power BI's **HTML Content** visual (by Daniel Marsh-Patrick) for fully custom, interactive-style charts.

**Supported `chart_type` values:**

| `chart_type` | Description |
|---|---|
| `"bar"` | Horizontal gauge-style bar chart |
| `"donut"` | SVG donut / ring chart with legend |
| `"kpi"` | KPI card with attainment % and progress bar |
| `"clustered_bar"` | Multi-series clustered horizontal bar chart |
| `"stacked_column"` | Vertical stacked column chart (SVG) |
| `"line"` | SVG polyline line / time-series chart |
| `"table"` | Styled HTML table with optional zebra striping |

**Key Args:**
- `port` — SSAS port from `list_instances()`
- `query` — DAX EVALUATE query
- `chart_type` — see table above
- `label_key` — column name for labels / X-axis categories
- `value_key` — column name for the primary numeric value
- `title` — chart title string
- `series_json` — JSON array for multi-series charts: `'[{"key":"Sales","label":"Net Sales","color":"#3b82f6"}]'`
- `value_prefix` / `value_suffix` — e.g. `"$"` or `" units"`
- `value_decimals` — decimal places in value labels
- `color` — primary colour for single-series charts (hex)
- `tmdl_path` *(optional)* — if set alongside `measure_name`, the HTML is written as a DAX measure
- `measure_name` *(optional)* — name for the TMDL measure

**Returns:**
```json
{
  "html": "<style>...</style><div>...</div>",
  "chart_type": "bar",
  "row_count": 12,
  "tmdl_result": "Successfully added measure 'Sales by Country' to Sales.tmdl"
}
```

#### Example Agent Workflow — HTML Bar Chart

```
1. list_instances()                     → port = "54321"
2. get_schema("54321")                  → find table "Sales", columns "Country", "Amount"
3. generate_html_visual(
     port="54321",
     query='EVALUATE SUMMARIZECOLUMNS("Sales"[Country], "Total", SUM("Sales"[Amount]))',
     chart_type="bar",
     label_key="Country",
     value_key="Total",
     title="Sales by Country",
     value_prefix="$",
     value_decimals=0,
     color="#10b981",
     tmdl_path="C:/path/Sales.SemanticModel/definition/tables/Sales.tmdl",
     measure_name="HTML Sales by Country"
   )
   → returns html + writes measure to TMDL
4. Add "HTML Content" visual to report page
5. Bind measure "HTML Sales by Country" to the visual's Values field
```

---

## 📊 HTML Visual Design System (`html_generators.py`)

All HTML visuals share a consistent design language:

- **Font:** Segoe UI (native Power BI font — no external loading)
- **Colors:** Professional Tailwind-inspired palette (`#3b82f6` blue, `#10b981` green, `#ef4444` red, `#f59e0b` amber)
- **CSS:** Fully inlined, scoped with short class names — no conflicts inside the HTML Content iframe sandbox
- **No dependencies:** Pure HTML + CSS + inline SVG — no external CDN, no JavaScript frameworks
- **Responsive:** Flex layouts that adapt to the visual container width

---

## ⚠️ Golden Rules for AI Agents (PBIR 2.0.0+ / TMDL)

> **For the definitive 6 Absolute Guardrails, see `framework/references/guardrails.md` or the orchestrator skill.**
> These additional rules complement the guardrails with technical implementation details.

### 1. PBIR Folder Structure for Visuals

Each visual must live in its own subfolder inside `visuals/`:

```
{project}.Report/
  definition/
    pages/
      {20-char-hex-page-id}/
        page.json
        visuals/
          {visual-name}/
            visual.json
```

### 2. HTML Content Visual — Binding the HTML Measure

To display a generated HTML visual in Power BI:
1. Add the **HTML Content** visual (by Daniel Marsh-Patrick) to the report page via AppSource.
2. In `visual.json`, set `"visualType": "htmlContent"` (or whichever identifier the visual uses).
3. Bind the DAX measure that returns the HTML string to the visual's `Values` field.
4. The visual renders the HTML inside a sandboxed iframe — no external script loading allowed.

### 3. Column vs. Measure Rule (CRITICAL)

Bar, column, line, combo, pie, donut charts, and treemaps **do not accept raw columns** on their value axis. Always define a DAX measure first via `add_measure_to_tmdl`, then reference it as a `"Measure"` projection in `visual.json`.

**Exception:** Table visuals (`tableEx`) accept direct column references.

### 4. Projection Keys by Chart Type

| Chart Type | Category key | Value key |
|---|---|---|
| Bar, Column, Line, Combo, Pie, Donut | `"Category"` | `"Y"` |
| Treemap | `"Group"` | `"Values"` |
| Table (`tableEx`) | — | `"Values"` |

### 5. TMDL Rules

- **Calculation Groups:** Adding any `calculationGroup` requires `discourageImplicitMeasures: true` in `model.tmdl`.
- **No `isKey: true`** on import dimension columns — causes cyclic reference errors in Power Query.
- **Double-quote `formatString`:** Always: `formatString: "$#,##0"` — unquoted symbols crash Power BI.
- **Duplicate check:** Scan the `.tmdl` file before inserting any measure.
- **Indentation:** Match the file's existing indentation (tabs vs. 2-space).

### 6. Workflow & Cache Rules

- **Close Power BI before edits:** Run `taskkill /IM PBIDesktop.exe /F` before modifying `.Report` or `.SemanticModel` files. An open instance will overwrite local changes.
- **Clear cache after major refactoring:** Delete `.SemanticModel/.pbi/cache.abf` after star-schema restructures or large model changes to avoid cached metadata conflicts.
- **No `.git` at drive root:** A `.git` folder at `C:\` or `D:\` causes Power BI's Git integration to crash with a permissions error.
- **Valid `visual.json` keys:** Never put `"size"`, `"config"`, or `"filters"` at the root — all dimensions go inside `"position"`.
- **Mandatory projection fields:** Every field projection must contain `"queryRef"` and `"nativeQueryRef"`.
- **Page folder names:** Must be 20-character lowercase hex strings or GUIDs — not descriptive names.

---

## 🔗 Credits & References

- [Power-BI-Visuals-Using-Claude-AI-HTML-DAX](https://github.com/Fasaclox/Power-BI-Visuals-Using-Claude-AI-HTML-DAX) — Fasaclox — pattern for DAX measures that return HTML strings for use in the HTML Content visual
- [HTML Content Visual](https://appsource.microsoft.com/en-us/product/power-bi-visuals/WA104380985) — Daniel Marsh-Patrick — the Power BI custom visual that renders HTML measures
- [Model Context Protocol](https://modelcontextprotocol.io) — Anthropic — open standard for tool-equipped AI agents
- [FastMCP](https://github.com/jlowin/fastmcp) — high-level Python framework for building MCP servers
