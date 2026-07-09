# Power BI Desktop Local MCP Server

Este es un servidor **Model Context Protocol (MCP)** desarrollado en Python que permite a agentes de Inteligencia Artificial (como Claude Desktop, Cursor, Cline, etc.) conectarse de forma local y dinámica a una instancia abierta de **Power BI Desktop** en Windows. 

A través de este servidor, el LLM puede descubrir tus reportes abiertos, inspeccionar el esquema de tus tablas y columnas, y ejecutar consultas DAX para interactuar con tus datos o generar visualizaciones dinámicas.

---

## Características

*   **Detección Dinámica de Puertos:** Power BI Desktop asigna un puerto aleatorio a Analysis Services cada vez que abre un archivo. Este servidor escanea automáticamente la carpeta `AppData` de Windows para encontrar los puertos activos de tus archivos `.pbix` o `.pbip` abiertos.
*   **Conexión Robusta mediante ADOMD.NET:** En lugar de depender de controladores OLE DB locales del sistema (`MSOLAP`) que suelen fallar por problemas de bits (32/64 bits) o actualizaciones, este servidor utiliza `pythonnet` para cargar directamente la biblioteca nativa `Microsoft.PowerBI.AdomdClient.dll` instalada por Power BI Desktop.
*   **Vistas del Esquema (Metadatos):** Permite extraer las tablas, columnas, tipos de datos y visibilidad de tu modelo de datos actual.
*   **Ejecución de DAX en JSON:** Permite ejecutar consultas DAX complejas (como `EVALUATE SUMMARIZECOLUMNS(...)`) y devuelve los resultados limpios y formateados en formato JSON serializable (manejando correctamente tipos numéricos y fechas de .NET).

---

## Estructura del Proyecto

*   `pbi_connector.py`: Módulo de conexión. Contiene la lógica para escanear puertos activos y la clase `PowerBIConnector` para consultar a la base de datos local usando ADOMD.NET.
*   `server.py`: Punto de entrada del servidor MCP. Define las herramientas usando la API de alto nivel `FastMCP`.
*   `requirements.txt`: Especificación de dependencias de Python.
*   `create_dashboard.py`: Script de utilidad complementario para generar un dashboard interactivo local en HTML con `Plotly` a partir de los datos de Power BI.

---

## Requisitos Previos

1.  **Sistema Operativo:** Windows (requerido para ejecutar Power BI Desktop y cargar las DLLs de .NET).
2.  **Python:** Versión 3.10 o superior.
3.  **Power BI Desktop:** Instalado en la ruta estándar de archivos de programa (`C:\Program Files\Microsoft Power BI Desktop`) o mediante la Microsoft Store.

---

## Instalación y Configuración

### 1. Clonar el Proyecto y Configurar Entorno
Navega a la carpeta del proyecto e instala las dependencias en un entorno virtual:

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Probar el Servidor en Consola
Con un archivo de Power BI Desktop abierto, puedes levantar el servidor MCP de forma interactiva en la consola usando `fastmcp`:

```powershell
fastmcp run server.py
```

---

## Registro en Clientes MCP (Claude, Cline, Cursor, etc.)

Para que tu cliente de Inteligencia Artificial pueda utilizar las herramientas de este servidor, debes registrarlo en tu archivo de configuración de MCP.

### Configuración (`mcp_config.json` o `claude_desktop_config.json`)

Agrega el siguiente bloque bajo la clave `mcpServers` (asegúrate de reemplazar las rutas absolutas por la ubicación real de tu proyecto):

```json
{
  "mcpServers": {
    "powerbi-local": {
      "command": "C:\\Ruta\\A\\Tu\\Proyecto\\powerbi-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Ruta\\A\\Tu\\Proyecto\\powerbi-mcp\\server.py"
      ]
    }
  }
}
```

---

## Herramientas Disponibles (MCP Tools)

Una vez cargado el servidor, el LLM tendrá acceso a las siguientes herramientas:

1.  **`list_instances`**:
    *   *Descripción:* Busca y devuelve los puertos de las instancias activas de Power BI Desktop abiertas actualmente en tu equipo.
    *   *Retorno:* Lista de diccionarios con la ruta del workspace temporal y el puerto local.
2.  **`get_schema`**:
    *   *Parámetros:* `port` (string)
    *   *Descripción:* Se conecta al puerto indicado y devuelve la lista de tablas y columnas que componen el modelo de datos.
3.  **`execute_dax`**:
    *   *Parámetros:* `port` (string), `query` (string)
    *   *Descripción:* Ejecuta una consulta DAX personalizada (`EVALUATE...`) y retorna los registros en formato JSON.
