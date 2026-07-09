# Power BI Desktop Local MCP Server

A Model Context Protocol (MCP) server that enables AI assistants (such as Claude Desktop, Cursor, Cline, and others) to securely and dynamically connect to locally running **Power BI Desktop** instances in Windows.

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
- `create_dashboard.py`: A companion script demonstrating how to run DAX queries, aggregate data in `pandas`, and generate a premium web-based dashboard with `Plotly`.

---

## Prerequisites

1. **Operating System:** Windows (required to run Power BI Desktop and load the native Windows .NET Assemblies).
2. **Python:** Version 3.10 or higher.
3. **Power BI Desktop:** Installed standard edition (`C:\Program Files\Microsoft Power BI Desktop`) or Microsoft Store edition.

---

## Installation & Setup

### 1. Environment Setup
Navigate to the project directory, initialize a virtual environment, and install dependencies:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Standalone Execution
With an active Power BI Desktop file open, you can test the MCP server locally in your terminal:

```powershell
fastmcp run server.py
```

---

## MCP Client Registration

To use this server inside your AI editor or chat client (e.g., Cursor, Cline, or Claude Desktop), register the server in your MCP configuration file.

### Configuration Configuration (`mcp_config.json` or `claude_desktop_config.json`)

Append the following block to your `mcpServers` object (ensure you replace paths with the absolute path of your workspace):

```json
{
  "mcpServers": {
    "powerbi-local": {
      "command": "C:\\Path\\To\\Your\\powerbi-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Path\\To\\Your\\powerbi-mcp\\server.py"
      ]
    }
  }
}
```

---

## MCP Tools Reference

The server exposes the following tools:

1. **`list_instances`**
   - *Description:* Detects and returns active local Power BI Desktop instances on the current machine.
   - *Returns:* List of objects containing the active local port and temporary directory path.

2. **`get_schema`**
   - *Parameters:* `port` (string)
   - *Description:* Connects to the local port and returns the semantic model table/column structure.

3. **`execute_dax`**
   - *Parameters:* `port` (string), `query` (string)
   - *Description:* Executes a custom DAX query (e.g., `EVALUATE 'Table'`) and returns rows formatted as JSON.

4. **`add_measure_to_tmdl`**
   - *Parameters:* `tmdl_path` (string), `name` (string), `expression` (string), `format_string` (string, optional)
   - *Description:* Appends a DAX measure directly to a local table's `.tmdl` file on disk. This guarantees the measure is permanently saved in the Power BI Project (PBIP) metadata instead of only living in the temporary active memory session.
