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

if __name__ == "__main__":
    mcp.run()
