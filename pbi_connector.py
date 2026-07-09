import os
import glob
import sys
from typing import List, Dict, Any

# Cargar pythonnet para utilizar el DLL oficial de Microsoft ADOMD Client
import clr

# Buscar el DLL de AdomdClient instalado por Power BI Desktop
dll_path = r"C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
if not os.path.exists(dll_path):
    # Fallback si no está en la ruta estándar (por ejemplo, versión de la Tienda de Microsoft)
    store_glob = r"C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop*\bin\Microsoft.PowerBI.AdomdClient.dll"
    matches = glob.glob(store_glob)
    if matches:
        dll_path = matches[0]

if os.path.exists(dll_path):
    sys.path.append(os.path.dirname(dll_path))
    clr.AddReference("Microsoft.PowerBI.AdomdClient")
else:
    raise FileNotFoundError("No se encontró el archivo DLL Microsoft.PowerBI.AdomdClient.dll. Asegúrate de tener Power BI Desktop instalado.")

from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdDataAdapter
from System.Data import DataSet

def get_active_pbi_instances() -> List[Dict[str, str]]:
    """
    Busca en AppData los puertos de las instancias activas de Power BI Desktop.
    Devuelve una lista de diccionarios con 'path' y 'port'.
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
                            try:
                                port = port_bytes.decode('utf-16').strip()
                            except Exception:
                                port = port_bytes.decode('utf-8', errors='ignore').strip()
                            port = ''.join(c for c in port if c.isdigit())
                            found_ports.append({
                                "path": data_path,
                                "port": port
                            })
                    except Exception:
                        pass
    
    return found_ports

class PowerBIConnector:
    def __init__(self, port: str):
        self.port = port
        self.connection_string = f"Provider=MSOLAP;Data Source=localhost:{self.port};"
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = AdomdConnection(self.connection_string)
            self.conn.Open()

    def disconnect(self):
        if self.conn:
            self.conn.Close()
            self.conn = None

    def execute_query(self, dax_query: str) -> List[Dict[str, Any]]:
        """
        Ejecuta un query DAX o DMV usando ADOMD y devuelve el resultado como una lista de diccionarios.
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
                    # Convertir DBNull a None de Python
                    if val.__class__.__name__ == 'DBNull':
                        row_dict[col] = None
                    else:
                        # Convertir tipos .NET comunes si es necesario a tipos estándar de Python
                        if type(val).__name__ == 'Decimal':
                            row_dict[col] = float(val)
                        else:
                            row_dict[col] = val
                results.append(row_dict)
                
            return results
        finally:
            self.disconnect()

    def get_model_schema(self) -> List[Dict[str, Any]]:
        """
        Obtiene las tablas y columnas del modelo de datos usando DMVs.
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
                        
                    dtype_map = {2: "String", 6: "Int64", 8: "Double", 9: "DateTime", 10: "Currency", 11: "Boolean"}
                    dtype_id = col.get("DataType", 2)
                    
                    schema[table_id]["Columns"].append({
                        "Name": name,
                        "DataType": dtype_map.get(dtype_id, str(dtype_id)),
                        "IsHidden": col.get("IsHidden", False)
                    })
                    
            return list(schema.values())
        except Exception as e:
            return [{"error": str(e), "message": "Fallo al consultar TMSCHEMA mediante ADOMD."}]
