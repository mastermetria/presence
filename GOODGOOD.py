import pandas as pd

# Chemins des fichiers source et destination
source_path = "3071_Ghepardo Marketing_Croix-Rouge_20241110_WITHDB_CONFIRMED.xlsm"
dest_path = "fundraising_template.xlsx"

# Nom des feuilles
source_sheet_name = "BA Payments New"  # Nom de la feuille source
dest_sheet_name = "Feuil1"    # Nom de la feuille destination

# Charger la feuille source
df = pd.read_excel(source_path, sheet_name=source_sheet_name)

# Charger le fichier destination existant
with pd.ExcelWriter(dest_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    # Copier le contenu dans la feuille de destination
    df.to_excel(writer, sheet_name=dest_sheet_name, index=False)

print(f"Les données de la feuille '{source_sheet_name}' ont été copiées dans la feuille '{dest_sheet_name}' de '{dest_path}'")
