# Power BI Desktop Local MCP Server

A Model Context Protocol (MCP) server that enables AI assistants (such as Claude Desktop, Cursor, Cline, Hermes, and others) to securely and dynamically connect to locally running **Power BI Desktop** instances in Windows.

Through this server, an LLM can discover open reports, inspect table and column schema (metadata), and execute custom DAX queries to interact with your data or generate visualizations dynamically.

---

## INSTALL THE MCP FOR YOUR AI AGENT WITH THIS PROMPT

Copy and paste this prompt when starting a new session with Cursor, Cline, Claude Desktop, or Hermes to have the agent configure the environment and understand the workflow automatically:

```
1. **Dependency Installation:** If the `.venv/` directory does not exist, initialize a Python virtual environment (`python -m venv .venv`), activate it, and install all dependencies declared in `requirements.txt`.
2. **Skill Registration:** Copy the `.agents/skills/powerbi-pbir-editor` customizations directory to your local global skills directory (e.g., in Hermes: `C:\Users\{User}\AppData\Local\hermes\skills\`).
3. **MCP Server Registration:** Register the `powerbi-local` MCP server in your global configuration file (e.g., in Hermes: `config.yaml`, in Cursor/Cline: `mcpjson.json`).
   - **CRITICAL:** Configure the command pointing to the Python executable of the local virtual environment (`.venv/Scripts/python.exe`) and the arguments pointing to the `launch.py` script of this repository. This prevents sys.path conflicts (PYTHONPATH pollution) when importing the `mcp` library.
4. **Understanding Your Capabilities (CRITICAL):** Do not assume you cannot create report pages or visuals programmatically just because the MCP tools don't have visual creation functions. You have full filesystem write access. You can and should create new pages and visuals by creating directories in the `.Report/definition/pages/` folder and writing `visual.json` files in their `visuals/` subfolders according to the `powerbi-pbir-editor` skill rules. Never tell the user you cannot create visuals; you can always write files.
5. **Next Steps (Request from Human):** Once the installation is complete, present the following next steps to the human to proceed:
   - "I have successfully installed and configured the Power BI MCP server and skills."
   - "Please open Power BI Desktop with your project."
   - "Provide me with the absolute path to your `.pbip` file and the name of the table you want to work with so I can start modeling and generating charts."
```

---

## Key Features

- **Dynamic Port Discovery:** Power BI Desktop spins up a local instance of SQL Server Analysis Services (SSAS) and assigns it a random port every session. This server automatically scans Windows `AppData` directories to identify active workspace sessions and resolve their local ports.
- **Robust Connection via ADOMD.NET:** Instead of relying on local system OLE DB providers (`MSOLAP`) which often suffer from architecture mismatches (32-bit vs. 64-bit) or missing drivers, this server leverages `pythonnet` to directly load the native `Microsoft.PowerBI.AdomdClient.dll` shipped with Power BI Desktop.
- **Schema Inspection:** Exposes database schema, detailing tables, columns, data types, and visibility states.
- **JSON-Safe DAX Execution:** Executes complex DAX expressions (e.g., `EVALUATE SUMMARIZECOLUMNS(...)`) and parses raw .NET data types (decimals, dates, nulls) into clean, JSON-serializable structures.
- **Self-Sanitizing Environment:** Automatically isolates its environment from host platforms (such as AI agent runners or global shells) by clearing contaminated `PYTHONPATH`/`PYTHONHOME` environment variables and prioritizing the local `.venv` directory to prevent runtime dependency import issues (e.g., `pywintypes` or `pythonnet` collision).

---

## Project Structure

- `pbi_connector.py`: Core database connector utilizing ADOMD.NET client libraries and local active port scanning.
- `server.py`: Entry point for the MCP server built with the high-level `FastMCP` framework.
- `requirements.txt`: Python package dependencies.
- `launch.py`: Sanitizing wrapper to run the server without PYTHONPATH collision.

---

## Prerequisites

1. **Operating System:** Windows (required to run Power BI Desktop and load the native Windows .NET Assemblies).
2. **Python:** Version 3.10 or higher.
3. **Power BI Desktop:** Installed standard edition (`C:\Program Files\Microsoft Power BI Desktop`) or Microsoft Store edition.

---

## Installation & Setup Step-by-Step

### 1. Clone & Set Up Workspace
Navigate to the directory and run:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Standalone Test
With Power BI Desktop open containing a loaded dataset:
```powershell
fastmcp run server.py
```

### 3. Register MCP Server in client (Cursor, Cline, Claude Desktop, Hermes)
Add the following block to your MCP config file (e.g. `C:\Users\{User}\AppData\Local\hermes\config.yaml` or `C:\Users\{User}\AppData\Roaming\Cursor\User\globalStorage\moe.etherelf.container\mcpjson.json`):

```yaml
# yaml format (Hermes config.yaml)
mcp_servers:
  powerbi-local:
    command: C:/Users/{User}/powerbi-mcp/.venv/Scripts/python.exe
    args:
      - C:/Users/{User}/powerbi-mcp/launch.py
    connect_timeout: 30
    timeout: 120
```

```json
// json format (Cursor / Cline config)
{
  "mcpServers": {
    "powerbi-local": {
      "command": "C:\\Users\\{User}\\powerbi-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\{User}\\powerbi-mcp\\launch.py"
      ]
    }
  }
}
```

---

## ⚠️ GOLDEN RULES FOR HUMAN AND AI AGENTS (PBIR 2.0.0+ / TMDL)

When creating or modifying Power BI report pages programmatically, you must follow these rules strictly. Failure to do so will result in **empty visual placeholders** or **report corruption**.

### 1. Folder Structure for Visuals (PBIR 2.0.0+)
In modern Power BI projects, visual files **must not** be placed directly in the page folder. They must be organized inside a `visuals/` subfolder, where each visual is its own directory containing a `visual.json` file:
```
{proyecto}.Report/
  definition/
    pages/
      {page-guid}/
        page.json
        visuals/
          {visual-name}/
            visual.json
```

### 2. Visual JSON Structure (visualContainer Schema)
Projections and fields must be structured directly under `visual.query.queryState` (never on the root of `visual.json` or directly under `visual`).

Example visual configuration (`visual.json`):
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.5.0/schema.json",
  "name": "treemap-servicio",
  "position": { "x": 20, "y": 20, "z": 0, "width": 610, "height": 310, "tabOrder": 0 },
  "visual": {
    "visualType": "treemap",
    "query": {
      "queryState": {
        "Group": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "comidasrapidas" } },
                  "Property": "nse"
                }
              },
              "queryRef": "comidasrapidas.nse",
              "nativeQueryRef": "nse"
            }
          ]
        },
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "comidasrapidas" } },
                  "Property": "Promedio Servicio"
                }
              },
              "queryRef": "comidasrapidas.Promedio Servicio",
              "nativeQueryRef": "Promedio Servicio"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true,
    "objects": {},
    "visualContainerObjects": {
      "title": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "text": { "expr": { "Literal": { "Value": "'Servicio por NSE'" } } }
          }
        }
      ]
    }
  }
}
```

### 3. Column vs Measure Rule (CRÍTICO)
- **Bar/Column/Line/Funnel/Pie/Donut Charts** and **Treemaps** **DO NOT** accept direct columns (`"Column"`) on their Y-axis/Values axis. Doing so will result in an **empty visual** showing the "Select or drag fields" warning.
- **Fix:** You must first define a DAX measure in the table's `.tmdl` file (using the MCP tool `add_measure_to_tmdl`), and reference it as a `"Measure"` projection in the visual JSON.
- **Table Visuals (`tableEx`):** Direct column references are only allowed in table visual projections (`"Values"` channel).

### 4. Projection Keys by Chart Type
- **Bar, Column, Line, Combo, Funnel, Pie, Donut:** Use `"Category"` (grouping) and `"Y"` (values/measure).
- **Treemaps:** Use `"Group"` (grouping) and `"Values"` (measure/size).
- **Tables (`tableEx`):** Use `"Values"` (array of column projections).

### 5. TMDL Measure Formatting
When appending measures to TMDL files:
- Double quote the `formatString` if it contains spaces or symbols (e.g., `formatString: "0.00"` or `formatString: "$#,##0"`). Unquoted strings with symbols will crash Power BI.
- Prevent duplicate measures by scanning the TMDL file before inserting.
- Always close Power BI Desktop (`taskkill /IM PBIDesktop.exe /F`) before editing.
