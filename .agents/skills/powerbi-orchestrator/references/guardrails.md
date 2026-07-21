# Power BI Absolute Guardrails

These 6 rules are NON-NEGOTIABLE.

1. NEVER create model.bim/TMDL from scratch. User must load data in PBID first.
2. ALWAYS close PBID before editing files: taskkill /IM PBIDesktop.exe /F
3. NEVER create visual.json manually. ALWAYS use: pbir add visual
4. TMDL requires LF (\\n), NOT CRLF (\\r\\n).
5. Delete cache.abf before reopening PBID.
6. Do NOT use % in DAX measure names. Use "Pct" instead.

## Quick Reference

| Violation | Symptom | Fix |
|-----------|---------|-----|
| CRLF in TMDL | InvalidLineType: Other line 1 | python fix_tmdl.py |
| Manual visual.json | NullReferenceException | Delete + pbir add visual |
| compatLevel 1650 | Unsupported level | Change to 1600 |
| Direct column in Y/Values | Empty rectangle | Create DAX measure |
| cache.abf not deleted | Theme won't apply | Delete file |
| show in page.json background | Schema error | Remove show |
| slicer wrong orientation | Items not showing | orientation=1 + responsive=false |
| % in measure name | Empty rectangle | Replace with Pct |
| formatString unquoted | PBID crash on open | python fix_tmdl.py |
| BOM in JSON | Load error | UTF-8 without BOM |
| name missing in visual.json | Property error | Add name to root |
