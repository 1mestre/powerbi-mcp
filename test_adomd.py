import clr
import sys
import os

dll_path = r"C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
if not os.path.exists(dll_path):
    print("DLL not found!")
    sys.exit(1)

sys.path.append(os.path.dirname(dll_path))
clr.AddReference("Microsoft.PowerBI.AdomdClient")

from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdDataAdapter
from System.Data import DataSet

port = "60393"
connection_string = f"Provider=MSOLAP;Data Source=localhost:{port};"

print("Connecting...")
try:
    conn = AdomdConnection(connection_string)
    conn.Open()
    print("Connected successfully!")
    
    cmd = conn.CreateCommand()
    cmd.CommandText = "SELECT * FROM $SYSTEM.TMSCHEMA_TABLES"
    adapter = AdomdDataAdapter(cmd)
    ds = DataSet()
    adapter.Fill(ds)
    
    tables = ds.Tables[0]
    print("Tables in model:")
    for row in tables.Rows:
        name = str(row["Name"])
        if not (name.startswith("RowNumber") or name.startswith("LocalDateTable") or name.startswith("DateTableTemplate")):
            print("-", name)
            
    conn.Close()
except Exception as e:
    print("Error:", e)
