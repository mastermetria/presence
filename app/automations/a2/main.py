from datetime import datetime
from genericpath import isdir
import time
import pandas as pd
import subprocess
import shutil
import json
import re
import os

from automations.decorator.logs import logs_history_factory

USER = 'tvanderdonck'       # ftp login
PASSWD = 'eZN7Rqd85L9q7h'   # ftp passwd
SERVER = '13.81.52.18'      # ftp host

A2_PATH = './automations/a2/'
DOWNLOADS_PATH = './automations/a2/downloads/'



def file_treatment(max_nb, file_list):
    
    commercial_template_path = f'{DOWNLOADS_PATH}commercial_template.xlsx'
    fundraising_template_path = f'{DOWNLOADS_PATH}fundraising_template.xlsx'

    # Nom des feuilles
    source_sheet_name = "BA Payments New"
    dest_sheet_name = "Feuil1"

    for file in file_list:
        source_file = f'{DOWNLOADS_PATH}{max_nb}/{file}'
        print(source_file)
        # Charger la feuille source
        df = pd.read_excel(source_file, sheet_name=source_sheet_name)

        c4_value = df.iloc[2, 2]

        # check the type of document -- fundraising OR commercial
        dest_path = fundraising_template_path if c4_value == 'Fundraising' else commercial_template_path

        # Charger le fichier destination existant
        with pd.ExcelWriter(dest_path,engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Copier le contenu dans la feuille de destination
            df.to_excel(writer, sheet_name=dest_sheet_name, index=False)


        # Copier le fichier avec un nom unique
        shutil.copyfile(
            dest_path,
            f'{DOWNLOADS_PATH}processed/{file}'
        )

    time.sleep(1)


def execute(command):  # function to execute command with subprocess
    try:
        result = subprocess.run(
            command, 
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # Ajout d'un timeout pour éviter les blocages
        )
        return result.stdout

    except subprocess.TimeoutExpired:
        print("La commande a pris trop de temps et a été arrêtée.")
        return "Error"


# *** Partie 1 - Récupérer les xlsx sur le serveur ftp ***

def ftp_mirror():
    current_year = datetime.now().year  # Année actuelle
    year_folder_ls_command = f'lftp -u {USER},{PASSWD} ftps://{SERVER} -e "set ssl:verify-certificate no; cd {current_year}; ls; bye"'
    year_folder_ls = execute(year_folder_ls_command)  # Exécuter la commande

    # Traiter la sortie et récupérer le dossier le plus récent
    folder_by_date = [int(date) for date in re.findall(r'\b\d{8}\b', year_folder_ls)]
    global last_date_folder
    last_date_folder = max(folder_by_date)

    global new_data_available
    new_data_available = False  # Initialisation du flag

    # Lire la valeur de last_date depuis db.json
    try:
        with open('db.json', 'r') as file:
            data = json.load(file)
            last_date = data["automations"][1]["test"]  # Accès direct à last_date
    except (FileNotFoundError, KeyError, IndexError, json.JSONDecodeError):
        last_date = None  # Considérer comme non traitée si problème

    # Comparer la date et télécharger si nécessaire
    if last_date is None or int(last_date) != last_date_folder:
        new_data_available = True
        day_folder_entry_command = f'lftp -u {USER},{PASSWD} ftps://{SERVER} -e "set ssl:verify-certificate no; cd {current_year}; lcd {DOWNLOADS_PATH}; mirror {last_date_folder}; ls; bye"'
        execute(day_folder_entry_command)
@logs_history_factory(1)
def run():
    print("start a2")
    if not os.path.isdir(f'{DOWNLOADS_PATH}processed') :
        os.makedirs(f'{DOWNLOADS_PATH}processed', exist_ok=True)

    list_processed = os.listdir(f'{DOWNLOADS_PATH}processed')
    for file in list_processed :
        os.remove(f'{DOWNLOADS_PATH}processed/{file}')
    ftp_mirror()
    time.sleep(1)

    file_treatment(last_date_folder, os.listdir(f'{DOWNLOADS_PATH}{last_date_folder}'))
