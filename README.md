# ⚡ Framework Power BI Hermes — Motor Multi-Agente para Dashboards PBIP y PBIR

[![Power BI PBIR](https://img.shields.io/badge/Power_BI-PBIP%20%7C%20PBIR%202.0-yellow?style=for-the-badge&logo=powerbi)](https://powerbi.microsoft.com/)
[![Versión del Framework](https://img.shields.io/badge/Framework-2.0.0--Gold-blue?style=for-the-badge)](https://github.com/1mestre/desktop-ssas-mcp)
[![Compatibilidad](https://img.shields.io/badge/Agentes-Hermes%20%7C%20Anti--Gravity%20%7C%20Claude%20%7C%20Cursor-green?style=for-the-badge)](https://github.com/1mestre/desktop-ssas-mcp)

El **Framework Power BI Hermes** es un conjunto de herramientas e instrucciones de ingeniería integral diseñado para capacitar a agentes de inteligencia artificial (**Hermes, Anti-Gravity, Claude Code, Cursor, Windsurf, Cline**) en la generación, modelado, maquetación y validación determinista de proyectos de Power BI (`.pbip` / `.pbir` / `.tmdl`) con calidad ejecutiva y en primera pasada.

---

## 🎯 ¿Qué es el Framework Power BI Hermes?

El framework integra 4 componentes clave para eliminar bucles infinitos de corrección, temas sin formato, solapamientos espaciales y archivos TMDL corruptos:

1. **Orquestador Maestro y 7 Sub-Skills Especializadas** (`.agents/skills/` y `~/.hermes/skills/`) para flujo de 8 fases, maquetación multipágina, inyección DAX y control de esquemas.
2. **Motor de Scripts de Verificación en Python** (`framework/scripts/`) para aplicación automática de temas, validación de contrastes WCAG, detección de colisiones por página y limpieza de saltos de línea LF.
3. **6 Guardrailes Absolutos y 5 Pilares Anti-Gravity** con reglas matemáticas estrictas para rejillas de 1280x720 (máximo 5 tarjetas KPI por fila, `ancho=232px`, `gap=20px`).
4. **Servidor MCP Local de SSAS** (`server.py` vía `launch.py` usando `powerbi-local`) para ejecutar consultas DAX en vivo y extraer esquemas directamente de instancias abiertas de Power BI Desktop en Windows.

---

## ⚡ Guía de Instalación y Activación Rápida

### 🤖 Opción A: Prompt Único para Cualquier Agente (Copiar y Pegar en el Chat)

```text
Tarea: Inicializar e instalar el Framework Power BI Hermes.

1. Clonar el repositorio: https://github.com/1mestre/desktop-ssas-mcp.git
2. Crear entorno virtual Python e instalar dependencias:
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
3. Cargar la skill de orquestación:
   - En Hermes: Ejecutar skill_view(name='powerbi-orchestrator')
   - En Anti-Gravity / Claude Code / Cursor: Copiar .agents/skills/* al directorio de skills activo y leer .agents/skills/powerbi-orchestrator/SKILL.md
4. Reglas de ejecución obligatoria:
   - En Fase 6: Ejecutar obligatoriamente: python framework/scripts/apply_theme.py "<Proyecto>.pbip" --theme slate-terracotta
   - En Fase 7: Ejecutar obligatoriamente: python framework/scripts/check_overlaps.py "<Proyecto>.Report"
5. Confirmar cuando el entorno esté listo para iniciar la creación del dashboard.
```

---

### 🔧 Opción B: Instalación Manual por Plataforma

#### 1. Instalación en Hermes (Perfil Local)
```powershell
xcopy /E /I /Y .agents\skills\* %LOCALAPPDATA%\hermes\skills\
```

#### 2. Instalación en Espacio de Trabajo (Anti-Gravity / Claude Code / Cursor / Windsurf)
```powershell
xcopy /E /I /Y .agents\skills\* .agents\skills\
```

#### 3. Configuración del Servidor MCP (Opcional para DAX en Vivo)

##### Configuración para Hermes (`config.yaml`)
```yaml
mcp_servers:
  powerbi-local:
    command: C:/ruta/a/desktop-ssas-mcp/.venv/Scripts/python.exe
    args:
      - C:/ruta/a/desktop-ssas-mcp/launch.py
    connect_timeout: 30
    timeout: 120
```

##### Configuración para Cursor / Cline / Windsurf (`mcp.json`)
```json
{
  "mcpServers": {
    "powerbi-local": {
      "command": "C:\\ruta\\a\\desktop-ssas-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\ruta\\a\\desktop-ssas-mcp\\launch.py"
      ]
    }
  }
}
```

---

## 📁 Estructura Completa del Repositorio

```text
desktop-ssas-mcp/
├── README.md                           # Guía de documentación e instalación en español
├── requirements.txt                    # Dependencias de Python (fastmcp, pythonnet, etc.)
├── launch.py                           # Aislador de entorno (evita conflictos de PYTHONPATH)
├── server.py                           # Servidor MCP (list_instances, get_schema, execute_dax, add_measure_to_tmdl, generate_html_visual)
├── pbi_connector.py                    # Conector ADOMD.NET y escáner de puertos SSAS
├── html_generators.py                  # Generadores de visuales HTML (barras, donas, KPIs, tablas)
├── fix_tmdl_format.py                  # Sanitizador de formatString en TMDL
├── new_powerbi_dashboard.py            # Suite de automatización en lote
├── framework/                          # 📦 Núcleo del Framework
│   ├── SKILL.md                        # Skill maestra del Framework
│   ├── DESIGN_GUIDELINES.md            # Guías de estética visual, WCAG y tokens de temas
│   ├── references/
│   │   └── guardrails.md               # 6 guardrailes pre-vuelo no negociables
│   └── scripts/                        # 🛠️ Motor de Scripts de Verificación
│       ├── apply_theme.py              # Motor de aplicación de temas y estilos (Modos Claro y Oscuro)
│       ├── check_overlaps.py           # Detector de solapamientos por página y límites de 1280x720
│       ├── validate_pbip.py            # Validador de estructura PBIP (54 comprobaciones)
│       ├── fix_tmdl.py                 # Corrector de saltos de línea LF, BOM y formato TMDL
│       ├── audit_csv.py                # Auditor de archivos CSV (BOM, comillas, delimitadores)
│       └── csv_fix.py                  # Limpiador programático de CSVs
└── .agents/
    └── skills/                         # 🤖 Suite de Skills para Agentes IA
        ├── powerbi-orchestrator/       # SKILL MAESTRA (Carga todas las sub-skills automáticamente)
        ├── powerbi-tmdl-modeling/      # Medidas DAX, sintaxis TMDL y preservación de particiones
        ├── powerbi-design-layout-themes/ # Rejilla 1280x720, matemática de KPIs y temas WCAG
        ├── powerbi-pbir-visuals-specs/  # Tipos de visuales, proyecciones y bloqueo de esquema 2.9.0
        ├── powerbi-pbir-troubleshooting/ # 5 Pilares Anti-Gravity y soluciones a trampas comunes
        ├── powerbi-visual-styling/      # Reglas específicas de fondos y tipografía por tipo de visual
        ├── powerbi-csv-audit/           # Auditoría de tubería de datos CSV
        └── pbir-dark-theme-styling/     # Plantillas JSON exactas para temas oscuros
```

---

## 🎯 Flujo de Trabajo Orquestado en 8 Fases

Todo agente que ejecute tareas con este framework DEBE seguir este flujo:

| Fase | Nombre | Descripción de la Tarea | Herramienta / Script de Validación |
|:---:|---|---|---|
| **0** | **Descubrimiento Interactivo** | Preguntar al usuario sobre origen de datos, audiencia y tema deseado. | `audit_csv.py` (si el origen es CSV) |
| **1** | **Verificación de Entorno** | Confirmar estructura PBIP y asegurar que Power BI Desktop esté cerrado. | `validate_pbip.py` |
| **2** | **Análisis del Modelo** | Inspeccionar esquemas de tablas y consultas DAX de muestra. | `get_schema()` / `execute_dax()` vía MCP |
| **3** | **Diseño Visual** | Seleccionar uno de los 5 temas premium y establecer la rejilla de páginas. | `powerbi-design-layout-themes` |
| **4** | **Modelado DAX** | Inyectar medidas DAX en archivos `.tmdl` (`newline='\n'`). | `fix_tmdl.py` |
| **5** | **Creación de Visuales** | Generar visuales usando `pbir add visual <tipo>` (nunca JSON manual). | CLI `pbir` |
| **6** | **Aplicación de Tema y Estilo** | **EJECUCIÓN OBLIGATORIA:** Aplicar tema y ajustar fondos en `page.json`. | `python scripts/apply_theme.py "<Proyecto>.pbip" --theme slate-terracotta` |
| **7** | **Verificación Final** | **EJECUCIÓN OBLIGATORIA:** Verificar 0 solapamientos y 52/54+ checks en PBIP. | `python scripts/check_overlaps.py` y `validate_pbip.py` |
| **8** | **Entrega al Usuario** | Eliminar `cache.abf` e indicar al usuario abrir el archivo `.pbip` en Power BI. | — |

---

## 🛡️ 6 Guardrailes Absolutos y 5 Principios Deterministas

### 🛑 6 Guardrailes Absolutos (Violación = Dashboard Roto)
1. **REGLA #1: NUNCA crear `model.bim` ni TMDL desde cero.** El usuario DEBE cargar los datos en Power BI Desktop y guardar como `.pbip`.
2. **REGLA #2: SIEMPRE cerrar Power BI Desktop antes de editar archivos.** Ejecutar `taskkill /IM PBIDesktop.exe /F`.
3. **REGLA #3: NUNCA crear `visual.json` manualmente.** Usar SIEMPRE `pbir add visual <tipo>`.
4. **REGLA #4: TMDL requiere estrictamente saltos de línea LF (`\n`), NUNCA CRLF (`\r\n`).** Usar en Python `open(..., newline='\n')`.
5. **REGLA #5: SIEMPRE borrar `cache.abf` antes de reabrir Power BI Desktop.** (`<Proyecto>.SemanticModel/.pbi/cache.abf`).
6. **REGLA #6: NUNCA usar `%` en nombres de medidas DAX.** Usar `Pct` en su lugar (`Avg Discount Pct`).

---

### ⚡ 5 Principios Deterministas de Estilo PBIR

| Principio | Regla Principal | Detalle de Implementación |
|---|---|---|
| **1. Custom Visual Binding** | Proyección dual en `queryState` | Duplicar proyecciones bajo `"Values"` Y el rol del manifiesto (`"content"` para HTML Content). |
| **2. Canvas Background** | Sobrescribir `page.json` directamente | Editar `objects.background` en `page.json`. **NUNCA incluir la propiedad `show` en `page.json`** (causa error de esquema). |
| **3. Color Key Mapping** | Claves exactas por tipo de visual | Tarjetas KPI:`labels`/`categoryLabels`, Donas:`labels`/`legend`, Barras:`dataPoint`/`labelColor`, Slicers:`items`/`header`. |
| **4. Multi-Color Bars** | Selectores `scopeId` en `dataPoint` | Inyectar array de comparación `scopeId`. La propiedad `Comparison.Right` lleva el `Literal` directo sin `expr` externo. |
| **5. Matemática de Rejilla 1280x720** | Rejilla rígida y límites por página | **Máximo 5-6 visuales por página.** **Máximo 5 KPIs por fila** (`ancho=232px`, `gap=20px`, `margen=20px`). Fórmula: $x_i = 20 + i \times 252$. |

---

## 🎨 Catálogo de 5 Temas Premium

El script `apply_theme.py` incluye 5 perfiles visuales completos para modos claro y oscuro:

| Nombre del Tema | Modo | Paleta Principal | Uso Recomendado |
|---|:---:|---|---|
| **`slate-terracotta`** | Oscuro | Lienzo `#0F3040`, Tarjetas `#1A4055`, Texto `#F8FAFC`, Acentos `#A56F63`, `#D99B7F` | **Ejecutivo / Financiero (Default)** |
| **`magenta-blossom`** | Claro | Lienzo `#FFFFFF`, Tarjetas `#F9FAFB`, Texto `#111827`, Acentos `#92003A`, `#F62477` | Marketing y Redes Sociales |
| **`ecotone-spring`** | Claro | Lienzo `#F5F2EB`, Tarjetas `#FAF8F3`, Texto `#1A1A2E`, Acentos `#769826`, `#A1CB35` | Medio Ambiente y Sostenibilidad |
| **`roasted-espresso`** | Oscuro | Lienzo `#1A0F0D`, Tarjetas `#2D1814`, Texto `#F8FAFC`, Acentos `#60241E`, `#E77B49` | Operaciones y Comercio Minorista |
| **`vintage-nordic`** | Claro | Lienzo `#EBEDE3`, Tarjetas `#F0F2E9`, Texto `#0B1849`, Acentos `#0B1849`, `#124D1C` | Reportes Corporativos y Formales |

---

## 🛠️ Referencia de los Scripts de Verificación

### 1. `apply_theme.py` (Motor de Estilos y Temas)
Aplica la transformación completa sobre `page.json`, `CY26SU05.json` y contenedores `visual.json`:
```powershell
python framework/scripts/apply_theme.py "F:/proyectos/Ventas.pbip" --theme slate-terracotta
```

### 2. `check_overlaps.py` (Detector de Solapamientos y Desbordamiento)
Revisa página por página que ningún visual se solape ni sobrepase el lienzo (1280x720px):
```powershell
python framework/scripts/check_overlaps.py "F:/proyectos/Ventas.pbip"
```

### 3. `validate_pbip.py` (Validador de Estructura PBIP)
Ejecuta 54 comprobaciones sobre `.pbip`, `.pbir`, `pages.json`, `visual.json` y archivos `.tmdl`:
```powershell
python framework/scripts/validate_pbip.py "F:/proyectos/Ventas.pbip"
```

### 4. `fix_tmdl.py` (Sanitizador de Archivos TMDL)
Fuerza saltos de línea LF (`\n`), elimina el BOM de UTF-8 y entrecomilla los `formatString`:
```powershell
python framework/scripts/fix_tmdl.py "F:/proyectos/Ventas.SemanticModel/definition/"
```

### 5. `audit_csv.py` (Auditor de Archivos CSV)
Audita archivos CSV de origen detectando comillas desbalanceadas, delimitadores inconsistentes y codificación:
```powershell
python framework/scripts/audit_csv.py "datos/ventas_raw.csv"
```

---

## 🔌 Herramientas MCP del Servidor Local (`powerbi-local`)

Cuando Power BI Desktop se ejecuta en Windows, el servidor MCP (`server.py`) expone estas 5 herramientas:

| Herramienta | Propósito | Formato de Salida |
|---|---|---|
| **`list_instances()`** | Escanea AppData local para detectar puertos SSAS activos de Power BI Desktop. | `[{"path": "...", "port": "54321"}]` |
| **`get_schema(port)`** | Extrae el esquema semántico completo (tablas, columnas, tipos de datos, medidas). | `[{"Name": "Ventas", "Columns": [...]}]` |
| **`execute_dax(port, query)`** | Ejecuta consultas DAX `EVALUATE` en vivo contra el motor SSAS activo. | `[{"Ventas[Pais]": "Mexico", "Total": 125000}]` |
| **`add_measure_to_tmdl(tmdl_path, name, expression, format_string)`** | Inyecta medidas DAX de forma segura en archivos `.tmdl` antes del bloque de partición. | Cadena de éxito / error |
| **`generate_html_visual(...)`** | Genera medidas visuales de HTML autocontenidas para el visual *HTML Content*. | `{"html": "...", "tmdl_result": "..."}` |

---

## 🔗 Créditos y Referencias

- [Guía oficial de Skill Creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) — Anthropic
- [Power-BI-Visuals-Using-Claude-AI-HTML-DAX](https://github.com/Fasaclox/Power-BI-Visuals-Using-Claude-AI-HTML-DAX) — Fasaclox
- [HTML Content Visual](https://appsource.microsoft.com/en-us/product/power-bi-visuals/WA104380985) — Daniel Marsh-Patrick
- [Model Context Protocol](https://modelcontextprotocol.io) — Anthropic
