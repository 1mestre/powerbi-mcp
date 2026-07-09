import os
import glob
import sys
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PowerBIConnector")

# Load pythonnet to interface with Microsoft ADOMD Client DLL
try:
    import clr
except ImportError:
    logger.error("pythonnet is not installed. Please install it using 'pip install pythonnet'.")
    raise

# Search for the AdomdClient DLL installed by Power BI Desktop
def _locate_adomd_dll() -> str:
    standard_path = r"C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
    if os.path.exists(standard_path):
        return standard_path
        
    # Store version fallback
    store_glob = r"C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop*\bin\Microsoft.PowerBI.AdomdClient.dll"
    matches = glob.glob(store_glob)
    if matches:
        return matches[0]
        
    raise FileNotFoundError(
        "Microsoft.PowerBI.AdomdClient.dll not found in standard paths. "
        "Please ensure Microsoft Power BI Desktop is installed."
    )

try:
    dll_path = _locate_adomd_dll()
    sys.path.append(os.path.dirname(dll_path))
    clr.AddReference("Microsoft.PowerBI.AdomdClient")
except Exception as e:
    logger.error(f"Failed to load ADOMD reference: {e}")
    raise

from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdDataAdapter
from System.Data import DataSet

def get_active_pbi_instances() -> List[Dict[str, str]]:
    """Scans local AppData workspaces to detect active Power BI Desktop instances and their local ports.

    Returns:
        List[Dict[str, str]]: List of dicts containing the workspace path and the local Analysis Services port.
    """
    base_paths = [
        os.path.expanduser(r"~\AppData\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"),
        os.path.expanduser(r"~\AppData\Local\Packages\Microsoft.MicrosoftPowerBIDesktop*\LocalCache\Local\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces")
    ]
    
    found_ports = []
    
    for base_path in base_paths:
        workspaces = glob.glob(base_path)
        for workspace in workspaces:
            data_folders = os.path.join(workspace, "*", "Data")
            for data_path in glob.glob(data_folders):
                port_file = os.path.join(data_path, "msmdsrv.port.txt")
                if os.path.exists(port_file):
                    try:
                        with open(port_file, 'rb') as f:
                            port_bytes = f.read()
                            # Handle UTF-16 LE encoding typically used by Windows
                            try:
                                port = port_bytes.decode('utf-16').strip()
                            except UnicodeDecodeError:
                                port = port_bytes.decode('utf-8', errors='ignore').strip()
                            
                            # Clean port string to contain digits only
                            port = ''.join(c for c in port if c.isdigit())
                            if port:
                                found_ports.append({
                                    "path": data_path,
                                    "port": port
                                })
                    except Exception as e:
                        logger.warning(f"Error reading port file at {port_file}: {e}")
                        
    return found_ports

class PowerBIConnector:
    """Manages connections and queries to a local Power BI Desktop Analysis Services instance."""

    def __init__(self, port: str):
        self.port = port
        self.connection_string = f"Provider=MSOLAP;Data Source=localhost:{self.port};"
        self.conn: Optional[AdomdConnection] = None

    def connect(self) -> None:
        """Establishes connection to the local Analysis Services instance."""
        if not self.conn:
            try:
                self.conn = AdomdConnection(self.connection_string)
                self.conn.Open()
            except Exception as e:
                logger.error(f"Failed to connect to local port {self.port}: {e}")
                raise

    def disconnect(self) -> None:
        """Closes the connection to the Analysis Services instance."""
        if self.conn:
            try:
                self.conn.Close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self.conn = None

    def execute_query(self, dax_query: str) -> List[Dict[str, Any]]:
        """Executes a DAX or DMV query against the active model.

        Args:
            dax_query (str): The query string.

        Returns:
            List[Dict[str, Any]]: List of dictionary rows matching the query results.
        """
        self.connect()
        try:
            cmd = self.conn.CreateCommand()
            cmd.CommandText = dax_query
            adapter = AdomdDataAdapter(cmd)
            ds = DataSet()
            adapter.Fill(ds)
            
            if ds.Tables.Count == 0:
                return []
                
            table = ds.Tables[0]
            columns = [str(col.ColumnName) for col in table.Columns]
            
            results = []
            for row in table.Rows:
                row_dict = {}
                for col in columns:
                    val = row[col]
                    # Handle DBNull values from .NET
                    if val.__class__.__name__ == 'DBNull':
                        row_dict[col] = None
                    else:
                        # Convert common .NET numeric types to Python native types
                        if type(val).__name__ == 'Decimal':
                            row_dict[col] = float(val)
                        else:
                            row_dict[col] = val
                results.append(row_dict)
                
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            self.disconnect()

    def get_model_schema(self) -> List[Dict[str, Any]]:
        """Retrieves semantic model schema including tables and their columns.

        Returns:
            List[Dict[str, Any]]: List of tables with their columns and data types.
        """
        try:
            tables_data = self.execute_query("SELECT * FROM $SYSTEM.TMSCHEMA_TABLES")
            columns_data = self.execute_query("SELECT * FROM $SYSTEM.TMSCHEMA_COLUMNS")
            
            schema = {}
            for table in tables_data:
                name = table.get("Name", "")
                if name.startswith("RowNumber") or name.startswith("LocalDateTable") or name.startswith("DateTableTemplate"):
                    continue
                table_id = table["ID"]
                schema[table_id] = {
                    "Name": name,
                    "Columns": []
                }
                
            for col in columns_data:
                table_id = col.get("TableID")
                if table_id in schema:
                    name = col.get("ExplicitName", col.get("InferredName", "")) or col.get("Name", "")
                    if not name or name.startswith("RowNumber"):
                        continue
                        
                    # Map standard TMSCHEMA data types
                    # 2: String, 6: Int64, 8: Double, 9: DateTime, 10: Currency, 11: Boolean
                    dtype_map = {
                        2: "String", 
                        6: "Int64", 
                        8: "Double", 
                        9: "DateTime", 
                        10: "Currency", 
                        11: "Boolean"
                    }
                    dtype_id = col.get("DataType", 2)
                    
                    schema[table_id]["Columns"].append({
                        "Name": name,
                        "DataType": dtype_map.get(dtype_id, str(dtype_id)),
                        "IsHidden": col.get("IsHidden", False)
                    })
                    
            return list(schema.values())
        except Exception as e:
            logger.error(f"Failed to retrieve model schema: {e}")
            return [{"error": str(e), "message": "Failed to query schema via ADOMD Client."}]
