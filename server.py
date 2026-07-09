from mcp.server.fastmcp import FastMCP
from pbi_connector import get_active_pbi_instances, PowerBIConnector

# Crear el servidor
mcp = FastMCP("PowerBI Desktop Local")

@mcp.tool()
def list_instances() -> list[dict]:
    """
    Busca y devuelve los puertos de las instancias activas de Power BI Desktop en la computadora actual.
    Cada instancia incluye la ruta de datos (que da una pista de qué archivo es) y el puerto local.
    """
    instances = get_active_pbi_instances()
    return instances

@mcp.tool()
def get_schema(port: str) -> list[dict]:
    """
    Se conecta a la instancia de Power BI en el puerto indicado y devuelve el esquema de datos (Tablas y Columnas).
    Usa el puerto devuelto por list_instances.
    """
    connector = PowerBIConnector(port)
    schema = connector.get_model_schema()
    return schema

@mcp.tool()
def execute_dax(port: str, query: str) -> list[dict]:
    """
    Ejecuta una consulta DAX (por ejemplo, EVALUATE 'Tabla') en la instancia de Power BI Desktop del puerto indicado
    y devuelve los resultados.
    """
    connector = PowerBIConnector(port)
    results = connector.execute_query(query)
    
    # Procesar resultados para asegurar serialización JSON
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

if __name__ == "__main__":
    mcp.run()
