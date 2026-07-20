import os
import sys

# Sanitize environment variables before any other imports.
# This prevents host environments (like AI agent runners, IDEs, or global shells)
# from injecting contaminating PYTHONPATH or PYTHONHOME variables, which can lead 
# to ModuleNotFoundErrors (e.g. with pywintypes/pythonnet).
for key in ['PYTHONPATH', 'PYTHONHOME']:
    os.environ.pop(key, None)

# Automatically resolve and prioritize local virtual environment packages if present.
base_dir = os.path.dirname(os.path.abspath(__file__))
venv_site_packages = os.path.join(base_dir, ".venv", "Lib", "site-packages")
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# ---------------------------------------------------------
# Standard MCP Imports
# ---------------------------------------------------------
from mcp.server.fastmcp import FastMCP
from pbi_connector import get_active_pbi_instances, PowerBIConnector

# Initialize FastMCP Server
mcp = FastMCP("PowerBI Desktop Local")

@mcp.tool()
def list_instances() -> list[dict]:
    """Scans and lists active local Power BI Desktop instances on the machine.

    Returns:
        list[dict]: Active Power BI instances with their local Analysis Services port and workspace path.
    """
    instances = get_active_pbi_instances()
    return instances

@mcp.tool()
def get_schema(port: str) -> list[dict]:
    """Retrieves the data model schema (tables and columns) from the specified Power BI Desktop port.

    Args:
        port (str): Local port of the active Power BI Desktop instance.

    Returns:
        list[dict]: Tables metadata and column details.
    """
    connector = PowerBIConnector(port)
    schema = connector.get_model_schema()
    return schema

@mcp.tool()
def execute_dax(port: str, query: str) -> list[dict]:
    """Executes a custom DAX query against the specified local Power BI Desktop instance.

    Args:
        port (str): Local port of the active Power BI Desktop instance.
        query (str): The DAX query (e.g. "EVALUATE 'TableName'").

    Returns:
        list[dict]: JSON-serializable list of row dictionaries matching the query results.
    """
    connector = PowerBIConnector(port)
    results = connector.execute_query(query)
    
    # Process results to guarantee JSON serializability for MCP
    clean_results = []
    for row in results:
        clean_row = {}
        for k, v in row.items():
            if v is None:
                clean_row[k] = None
            elif type(v).__name__ == 'Decimal':
                clean_row[k] = float(v)
            elif 'time' in type(v).__name__.lower() or 'date' in type(v).__name__.lower():
                clean_row[k] = str(v)
            else:
                clean_row[k] = v
        clean_results.append(clean_row)
        
    return clean_results

@mcp.tool()
def add_measure_to_tmdl(tmdl_path: str, name: str, expression: str, format_string: str = None) -> str:
    """Adds a DAX measure directly to a TMDL semantic model table file on disk.
    This ensures the measure is permanently saved in the Power BI Project (.pbip)
    and won't be lost when Power BI Desktop closes.

    Args:
        tmdl_path (str): Absolute path to the .tmdl file of the table (e.g. path/to/table.tmdl).
        name (str): The name of the new measure (e.g. "Total Sales").
        expression (str): The DAX formula (e.g. "SUM('Sales'[Amount])").
        format_string (str, optional): Format string for the measure (e.g. "$#,##0").

    Returns:
        str: Success or error message.
    """
    import os
    if not os.path.exists(tmdl_path):
        return f"Error: TMDL file not found at {tmdl_path}"
        
    try:
        with open(tmdl_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Standardize check for duplicate measure name
        if f"measure '{name}'" in content or f"measure {name}" in content:
            return f"Error: Measure '{name}' already exists in this TMDL file."
            
        # Detect indentation (tabs vs spaces)
        indent = "\t"
        if "\n  column" in content:
            indent = "  "
            
        measure_def = f"\n{indent}measure '{name}' = {expression}"
        if format_string:
            clean_format = format_string.strip()
            if not (clean_format.startswith('"') and clean_format.endswith('"')) and not (clean_format.startswith("'") and clean_format.endswith("'")):
                clean_format = f'"{clean_format}"'
            measure_def += f"\n{indent}{indent}formatString: {clean_format}"
        measure_def += "\n"
        
        partition_str = f"\n{indent}partition "
        if partition_str in content:
            parts = content.split(partition_str, 1)
            new_content = parts[0] + measure_def + partition_str + parts[1]
        else:
            annotation_str = f"\n{indent}annotation "
            if annotation_str in content:
                parts = content.split(annotation_str, 1)
                new_content = parts[0] + measure_def + annotation_str + parts[1]
            else:
                new_content = content.rstrip() + "\n" + measure_def
                
        with open(tmdl_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return f"Successfully added measure '{name}' to {os.path.basename(tmdl_path)}"
    except Exception as e:
        return f"Error modifying TMDL file: {e}"

@mcp.tool()
def generate_html_visual(
    port: str,
    query: str,
    chart_type: str,
    label_key: str,
    value_key: str,
    title: str = "",
    series_json: str = "",
    value_prefix: str = "",
    value_suffix: str = "",
    value_decimals: int = 0,
    color: str = "#3b82f6",
    tmdl_path: str = "",
    measure_name: str = "",
) -> dict:
    """Executes a DAX query, generates a self-contained HTML visual, and optionally
    writes it as a DAX measure to a TMDL file.

    Inspired by the Power-BI-Visuals-Using-Claude-AI-HTML-DAX project (Fasaclox pattern):
    measures that return HTML strings are rendered inside Power BI's "HTML Content" visual
    (by Daniel Marsh-Patrick), enabling fully custom charts without external visuals.

    Supported chart_type values
    ---------------------------
      "bar"            - Horizontal gauge-style bar chart
      "donut"          - SVG donut / ring chart
      "kpi"            - KPI card with attainment progress bar (requires value_key=actual, and
                         pass target via series_json: '[{"key":"<target_col>"}]')
      "clustered_bar"  - Multi-series clustered horizontal bar chart
      "stacked_column" - Vertical stacked column chart
      "line"           - SVG polyline line/time-series chart
      "table"          - Styled HTML table

    Args:
        port (str):            Local SSAS port from list_instances().
        query (str):           DAX EVALUATE query to pull the data.
        chart_type (str):      One of the supported types listed above.
        label_key (str):       Column name used as the category label / X-axis.
        value_key (str):       Primary column name for values / Y-axis.
        title (str):           Chart/card title displayed in the visual.
        series_json (str):     JSON array of series objects for multi-series charts.
                               Each item: {"key":"col","label":"Name","color":"#hex"}.
                               For "kpi" chart_type, pass [{"key":"<target_column>"}].
        value_prefix (str):    Prefix for numeric labels (e.g. "$").
        value_suffix (str):    Suffix for numeric labels (e.g. " units").
        value_decimals (int):  Decimal places in numeric labels.
        color (str):           Primary bar/fill colour for single-series charts.
        tmdl_path (str):       Optional. Absolute path to a .tmdl file. If provided
                               together with measure_name, the HTML string is written
                               directly as a DAX measure to the TMDL file.
        measure_name (str):    Name for the DAX measure written to TMDL (optional).

    Returns:
        dict with keys:
          "html"         - The complete HTML string.
          "chart_type"   - The chart type used.
          "row_count"    - Number of data rows processed.
          "tmdl_result"  - Result message from add_measure_to_tmdl (or "" if not used).
    """
    import json as _json
    from html_generators import (
        gen_bar_chart,
        gen_donut_chart,
        gen_kpi_card,
        gen_clustered_bar,
        gen_stacked_column,
        gen_line_chart,
        gen_html_table,
    )

    # --- Execute DAX query ---
    connector = PowerBIConnector(port)
    raw = connector.execute_query(query)

    # Sanitize to JSON-safe types
    data = []
    for row in raw:
        clean = {}
        for k, v in row.items():
            if v is None:
                clean[k] = None
            elif type(v).__name__ == 'Decimal':
                clean[k] = float(v)
            elif 'time' in type(v).__name__.lower() or 'date' in type(v).__name__.lower():
                clean[k] = str(v)
            else:
                clean[k] = v
        data.append(clean)

    # Parse optional series JSON
    series = []
    if series_json:
        try:
            series = _json.loads(series_json)
        except _json.JSONDecodeError:
            pass

    # --- Generate HTML ---
    html = ""
    ct = chart_type.lower().strip()

    if ct == "bar":
        html = gen_bar_chart(
            data=data, label_key=label_key, value_key=value_key,
            title=title, color=color,
            value_prefix=value_prefix, value_suffix=value_suffix,
            value_decimals=value_decimals,
        )

    elif ct == "donut":
        colors = [s.get("color", "#3b82f6") for s in series] if series else None
        html = gen_donut_chart(
            data=data, label_key=label_key, value_key=value_key,
            title=title, colors=colors,
        )

    elif ct == "kpi":
        # Expects data to have exactly one row with actual and target columns.
        # Pass target column name via series_json: [{"key": "target_col_name"}]
        row = data[0] if data else {}
        actual = float(row.get(value_key, 0) or 0)
        target_key = series[0]["key"] if series else value_key
        target = float(row.get(target_key, 0) or 0)
        html = gen_kpi_card(
            value=actual, target=target, label=title,
            value_prefix=value_prefix, value_suffix=value_suffix,
            value_decimals=value_decimals,
        )

    elif ct == "clustered_bar":
        if not series:
            series = [{"key": value_key, "label": value_key, "color": color}]
        html = gen_clustered_bar(
            data=data, label_key=label_key, series=series, title=title,
        )

    elif ct == "stacked_column":
        if not series:
            series = [{"key": value_key, "label": value_key, "color": color}]
        html = gen_stacked_column(
            data=data, label_key=label_key, series=series, title=title,
        )

    elif ct == "line":
        if not series:
            series = [{"key": value_key, "label": value_key, "color": color}]
        html = gen_line_chart(
            data=data, x_key=label_key, series=series, title=title,
        )

    elif ct == "table":
        cols = None
        if series:
            cols = series  # series items act as column descriptors
        html = gen_html_table(data=data, columns=cols, title=title)

    else:
        html = f"<div style='font-family:Segoe UI;padding:12px;color:#ef4444'>Unknown chart_type: {chart_type}</div>"

    # --- Optionally write to TMDL ---
    tmdl_result = ""
    if tmdl_path and measure_name and html:
        # Escape the HTML string for embedding in a DAX string literal
        dax_string = html.replace('"', '""')
        expression = f'"{dax_string}"'
        tmdl_result = add_measure_to_tmdl(
            tmdl_path=tmdl_path,
            name=measure_name,
            expression=expression,
        )

    return {
        "html":        html,
        "chart_type":  chart_type,
        "row_count":   len(data),
        "tmdl_result": tmdl_result,
    }

if __name__ == "__main__":
    mcp.run()
