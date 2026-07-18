---
name: powerbi-tmdl-modeling
description: Rules and guidelines for TMDL measure definitions, DAX formatting, partition preservation, and SSAS tabular engine constraints.
---

# Power BI TMDL Model & Measure Developer Skill

Use this skill when appending DAX measures, editing model properties, or modifying Tabular Model Definition Language (TMDL) files in Power BI Semantic Models (`.SemanticModel` directory).

---

## 1. TMDL Syntax & Comments Rules

* **TMDL Comments (CRITICAL):** TMDL only supports `//` for single-line comments. **NEVER use `--` (SQL-style double-dash)** — the TMDL parser will throw `InvalidLineType: Other` at the comment line. Power BI Desktop will fail to load with *"Error de formato TMDL: Tipo de línea inesperado: Other"*. If you must comment, omit comments entirely or use `//`.
* **Double-Quoting Format Strings:** If `formatString` contains spaces, currencies, or symbols, **always** enclose it in double quotes:
  - `formatString: "$#,##0"` (Correct)
  - `formatString: $#,##0` (Incorrect - will crash Power BI on open)
  - Use [fix_tmdl_format.py](file:///C:/Users/Sebas/desktop-ssas-mcp/fix_tmdl_format.py) to automatically fix unquoted format strings across `.tmdl` files.

---

## 2. Model Properties & Engine Constraints

* **`discourageImplicitMeasures` Setting (CRITICAL):** If the model defines any Calculation Group (`calculationGroup`), you **MUST** set the property `discourageImplicitMeasures: true` under `model Model` in `model.tmdl`. Failure to do so will result in a load crash in Power BI Desktop.
* **Avoid `isKey` on Dimensions (CRITICAL):** Do not add `isKey: true` to primary key columns of standard import tables (like date or dimension tables). It can cause *"a cyclic reference was found during evaluation"* errors in Power Query. Use model-level relationships to map the keys.
  - **Transient Evaluation Cache Bug:** Even when the model schema is 100% correct, Power BI Desktop may occasionally display a false-positive *"Se encontró una referencia cíclica durante la evaluación"* (A cyclic reference was found during evaluation) error on first open or first refresh due to a corrupted memory cache in the engine. This is a known Power BI bug. **Solution:** Tell the user to simply click the **Actualizar (Refresh)** button a second time, or close and reopen Power BI Desktop. The second load always completes successfully.
* **Partition Preservation (CRITICAL):** **NEVER** modify or delete the `partition {table} = m` block or the `annotation PBI_ResultType = Table` block located at the bottom of the `.tmdl` file. Deleting the partition block will cause a fatal load crash in Power BI Desktop with the error: `"Todas las tablas deben contener al menos una partición con la propiedad Full DataView"`. Any automated regex or parsing scripts to wipe/add measures must leave the partition block untouched.

---

## 3. DAX Naming & Measure Creation Guidelines

* **Avoid `%` in Measure Names (CRITICAL):** The `%` character in DAX measure names (even inside TMDL single quotes) causes grouped charts (`columnChart`, `barChart`, etc.) to render as **empty rectangles**. Power BI's internal engine interprets the `%` as a modulus operator or format specifier rather than a literal character.
  - **Fix:** Use `Pct` instead of `%` in all measure names:
    - `measure 'Avg Discount %'` ❌ -> `measure 'Avg Discount Pct'` ✅
* **Duplicate Prevention:** Always check if the measure name already exists in the `.tmdl` file to avoid compiling duplicates.
* **Measure Binding in PBIR:** Grouped charts require measure projections instead of raw column references. When you create a DAX measure in `.tmdl`, reference it in PBIR visual JSON using the `"Measure"` projection type (see [powerbi-pbir-visuals-specs](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-visuals-specs/SKILL.md)).

---

## 4. SSAS Live Query Execution & Inspection

To inspect the existing tabular model metadata or test DAX expressions live against running Power BI Desktop instances:
* Use the local MCP server tools in [server.py](file:///C:/Users/Sebas/desktop-ssas-mcp/server.py): `get_schema`, `list_databases`, and `execute_dax`.
* The underlying connection is managed by [pbi_connector.py](file:///C:/Users/Sebas/desktop-ssas-mcp/pbi_connector.py), which uses `Microsoft.PowerBI.AdomdClient.dll` to execute DAX queries programmatically.

---

## 🔗 RELATED SKILLS & REPOSITORY FILES

- 🏠 **[powerbi-pbir-editor](file:///C:/Users/Sebas/desktop-ssas-mcp/.agents/skills/powerbi-pbir-editor/SKILL.md)** - Master Skill Hub
- 🛠️ **[fix_tmdl_format.py](file:///C:/Users/Sebas/desktop-ssas-mcp/fix_tmdl_format.py)** - Python script to sanitize unquoted TMDL format strings
- 🔌 **[pbi_connector.py](file:///C:/Users/Sebas/desktop-ssas-mcp/pbi_connector.py)** - ADOMD.NET connector for local SSAS engine
- ⚡ **[server.py](file:///C:/Users/Sebas/desktop-ssas-mcp/server.py)** - FastMCP server for executing DAX and inspecting model schema
