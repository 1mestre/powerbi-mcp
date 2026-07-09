import re

tmdl_path = r"C:\Users\Sebas\Desktop\prueba.SemanticModel\definition\tables\Base_Datos_Consolidada.tmdl"

with open(tmdl_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
modified = 0

for line in lines:
    # Match lines like: \t\tformatString: $#,##0 or   formatString: 0.0%
    match = re.match(r"^(\s+formatString:\s+)(.+)$", line)
    if match:
        prefix, val = match.groups()
        val = val.strip()
        # If not already quoted
        if not (val.startswith('"') and val.endswith('"')) and not (val.startswith("'") and val.endswith("'")):
            # Enclose in double quotes
            new_line = f"{prefix}\"{val}\"\n"
            new_lines.append(new_line)
            modified += 1
            print(f"Modified: {line.strip()} -> {new_line.strip()}")
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

if modified > 0:
    with open(tmdl_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Successfully updated {modified} formatString values in TMDL file.")
else:
    print("No format strings needed updating.")
