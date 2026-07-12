# Power BI Desktop Local MCP Server

A Model Context Protocol (MCP) server that enables AI assistants (such as Claude Desktop, Cursor, Cline, Hermes, and others) to securely and dynamically connect to locally running **Power BI Desktop** instances in Windows.

Through this server, an LLM can discover open reports, inspect table and column schema (metadata), and execute custom DAX queries to interact with your data or generate visualizations dynamically.

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

---

## 🤖 AI Agent Bootstrapping Prompt (Prompt de Inicialización para Agentes)

Copia y pega este prompt al iniciar un nuevo chat con Cursor, Cline, Claude Desktop o Hermes para que configuren el entorno y entiendan el flujo de trabajo automáticamente:

```
Eres un agente de IA experto en desarrollo. Por favor, instala y configura de forma autónoma el servidor MCP 'powerbi-local' y el skill 'powerbi-pbir-editor' de este repositorio:

1. **Instalación de Dependencias:** Si no existe la carpeta `.venv/`, inicializa un venv de Python (`python -m venv .venv`), actívalo e instala las dependencias declaradas en `requirements.txt`.
2. **Registro de la Skill:** Copia la carpeta de personalizaciones `.agents/skills/powerbi-pbir-editor` a tu directorio local de skills globales (ej. en Hermes: `C:\Users\{User}\AppData\Local\hermes\skills\`).
3. **Registro del Servidor MCP:** Registra el MCP `powerbi-local` en tu archivo de configuración global (ej. en Hermes: `config.yaml`, en Cursor/Cline: `mcpjson.json`).
   - **CRÍTICO:** Configura el comando apuntando al ejecutable de Python de la carpeta virtual local (`.venv/Scripts/python.exe`) y los argumentos apuntando al archivo `launch.py` de este repositorio. Esto evitará conflictos de sys.path (PYTHONPATH pollution) al cargar la librería `mcp`.
4. **Próximos Pasos (Entregar al Humano):** Cuando completes la instalación, preséntale al humano los siguientes pasos para continuar:
   - "He instalado y configurado el servidor MCP y las skills de Power BI con éxito."
   - "Por favor, abre Power BI Desktop con tu proyecto."
   - "Proporcióname la ruta absoluta del archivo `.pbip` y el nombre de la tabla con la que deseas trabajar para comenzar a modelar y generar gráficos."
```

