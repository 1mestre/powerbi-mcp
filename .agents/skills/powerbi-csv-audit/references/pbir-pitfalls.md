# Power BI PBIR Operational Traps (Reference)

## pbir CLI UTF-8 Encoding Bug
**Symptom:** Titles with accented characters render as mojibake: `Total Títulos` → `Total TÃ­tulos`, `Películas` → `PelÃ­culas`.

**Root cause:** `pbir add visual --from-json` reads the JSON with ANSI/Latin-1 encoding instead of UTF-8, writing double-encoded bytes into visual.json title literals.

**Fix:** Always post-process visual.json files after creation:
```python
fixes = {"TÃ­tulos": "Títulos", "PelÃ­culas": "Películas", "PaÃ­ses": "Países"}
for vis in visual_dirs:
    path = f"{base}/{vis}/visual.json"
    content = open(path, 'r', encoding='utf-8').read()
    for wrong, correct in fixes.items():
        content = content.replace(wrong, correct)
    json.dump(json.loads(content), open(path, 'w'), indent=2, ensure_ascii=False)
```

## add_measure_to_tmdl Reintroduces CRLF
**Symptom:** After injecting measures via `mcp__powerbi_local__add_measure_to_tmdl`, `fix_tmdl.py` reports CRLF on previously clean files.

**Fix:** Always run `fix_tmdl.py` on the entire `definition/` directory after EVERY batch of measure injections.

## Golden Rule Clarification
Applies ONLY to Y-axis/Values role. Category accepts direct columns:
- ✅ Category → direct column fine
- ❌ Y/Values → MUST use DAX measure or aggregation
