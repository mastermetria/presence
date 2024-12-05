from flask_migrate import current
from db_utils import get_automation_by_id, update_automation_status
from models import Automation # Import de ton modèle SQLAlchemy
from automations.decorator.logs import logs_history_factory
from extensions import timer

from datetime import datetime
from dotenv import load_dotenv
import time
import pandas as pd
import requests
import subprocess
import shutil
import json
import re
import os

load_dotenv()


USER = os.getenv('A2_FTP_LOGIN')      # ftp login
PASSWD = os.getenv('A2_FTP_PASSWORD')   # ftp passwd
SERVER = os.getenv('A2_FTP_SERVER')      # ftp host
APP_PORT = os.getenv('APP_PORT') # app port

A2_PATH = './automations/a2/'
DOWNLOADS_PATH = './automations/a2/downloads/'

folder_dict = {
    "APEX": "APEX2",
    "DAY 1": "DAY1",
    "DLG CORPORATION": "DLGCORP",
    "EMPOWER CORP": "EMPOWER",
    "GHEPARDO": "GHEPARDO",
    "GRAVITY MARKETING": "GRAVITY",
    "KYS": "KYS",
    "REVIVAL": "REVIVAL",
    "REWARD PARTNERS": "REWARDPAR",
    "SLS DIVISION": "SLSDIVISIO",
    "VICTORY MARKETING": "VICTORYMAR"
}

JOURNAL = "TEST"


# -- INITIALIZATION --
def get_uuid():
        
    url = "https://isuite.antaris.fr/CNX/api/v1/authentification"

    payload = json.dumps({
        "Identifiant": "OPPY",
        "MotDePasse": "OPPY123*"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    ##################################################-- GET UUID --################################################
    # Effectuer la requête                                                                                         #
    response = requests.request("POST", url, headers=headers, data=payload)                          #

    # Vérifier si la réponse est correcte
    if response.status_code == 200:
        try:
            # Convertir la réponse en JSON
            response_json = response.json()
            # Récupérer la clé UUID
            UUID = response_json.get('UUID')  # Utilisez .get() pour éviter une KeyError si la clé n'existe pas
            if UUID:
                print(f"UUID: {UUID}")
            else:
                print("Clé 'UUID' non trouvée dans la réponse.")
        except json.JSONDecodeError:
            print("Erreur : la réponse n'est pas un JSON valide.")
    else:                                                                                                          #
        print(f"Erreur HTTP : {response.status_code}, {response.text}")                                            #
    ##################################################-- GET UUID --################################################
    return UUID





def extract_blocks_from_excel(file_path, sheet_name="Feuil2", bloc_column_index=3):
    """
    Extrait les blocs d'un fichier Excel basé sur une colonne spécifique.

    Args:
        file_path (str): Chemin vers le fichier Excel.
        sheet_name (str): Nom de la feuille à utiliser (par défaut "Feuil2").
        bloc_column_index (int): Index de la colonne utilisée pour regrouper les blocs (par défaut 3).

    Returns:
        list: Liste où chaque index est un bloc, contenant les lignes du bloc.
    """
    # Charger le fichier Excel sans en-têtes
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # Initialiser les variables pour déterminer la plage d'intérêt
    isdata = True
    max_row = 0

    # Parcourir la colonne indexée à `bloc_column_index` pour déterminer jusqu'où lire
    while isdata:
        valeur = str(df.iloc[max_row, bloc_column_index])  # Lire la valeur
        if re.match(r'^\d+\s+commis\. brutes$', valeur):  # Matcher le motif spécifique
            isdata = False  # Arrêter si on trouve la valeur correspondant au motif
        else:
            max_row += 1  # Continuer jusqu'à trouver la fin

    # Filtrer les données jusqu'à la ligne `max_row`
    filtered_df = df.iloc[:max_row]

    # Filtrer les lignes valides (où la colonne des blocs n'est pas NaN)
    filtered_df = filtered_df[filtered_df.iloc[:, bloc_column_index].notna()]

    # Grouper les blocs par la colonne choisie (index `bloc_column_index`)
    grouped_data = filtered_df.groupby(filtered_df.iloc[:, bloc_column_index])

    # Créer une liste où chaque index correspond à un bloc (liste de listes)
    # Convertir toutes les valeurs en types compatibles avec JSON
    result = [
        group.astype(str).values.tolist()  # Convertir toutes les données en chaînes
        for _, group in grouped_data
    ]

    return result


def send_data(file_path, uuid, folder):

    ##################################################-- CONNECT TO RIGHT folder --###############################
                                                                                                                    #
    url = "https://isuite.antaris.fr/CNX/api/v1/sessions/dossier"                                                   #

    payload = json.dumps(folder)
    headers = {
        'accept': 'text/plain',
        'UUID': uuid,
        'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload)                                      #
                                                                                                                    #
    ##################################################-- CONNECT TO RIGHT FOLDER --##################################

    blocks = extract_blocks_from_excel(file_path)

    for block in blocks:

        writing_line = []

        for line in block:

            writing_line.append({
                "Jour": int(line[0].split('-')[2]),
                "NumeroPiece": "",
                "NumeroFacture": "",
                "Compte": line[2],
                "CodeTVA": "",
                "Libelle": line[3],
                "Credit": round(float(line[5]), 2) if line[5] != "nan" else 0,
                "Debit": round(float(line[4]), 2) if line[4] != "nan" else 0,
                "ModeReglement": "",
                "ReferenceGed": ""
            })

        if  'F' in line[2]: # Vérifie si c'est un compte fournisseur
            url = "https://isuite.antaris.fr/CNX/api/v1/compta/comptes/fournisseur"

            payload = json.dumps({
            "Code": line[2],
            "Lib": " ".join(line[3].split()[1:3]),
            "Let": "",
            "CptHTAssocie": ""
            })
            headers = {
            'accept': 'text/plain',
            'UUID': 'GSEA6WRA91B7EKG9MYCYB4ZCT007TC',
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)


        # Construire une structure JSON directement
        data = {
            "Journal": JOURNAL,
            "Mois": int(line[0].split('-')[1]),
            "Annee": int(line[0].split('-')[0]),
            "ReferenceGed": "",
            "LignesEcriture": writing_line,
            "Periode": {
                "DateDebut": "2024-12-03T07:17:52.833Z",
                "DateFin": "2024-12-03T07:17:52.833Z"
            }
        }


        url = "https://isuite.antaris.fr/CNX/api/v1/compta/ecriture"

        payload = json.dumps(data)
        headers = {
        'accept': 'text/plain',
        'UUID': 'GSEA6WRA91B7EKG9MYCYB4ZCT007TC',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

@timer.track(time_saved=900.0)
def file_treatment(max_nb, file_list, uuid):
    
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
        folder = df.iloc[1,2].upper()
        # check the type of document -- fundraising OR commercial
        dest_path = fundraising_template_path if c4_value == 'Fundraising' else commercial_template_path

        # Charger le fichier destination existant
        with pd.ExcelWriter(dest_path,engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Copier le contenu dans la feuille de destination
            df.to_excel(writer, sheet_name=dest_sheet_name, index=False)

        # send_data(dest_path, uuid, folder)


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

def ftp_mirror(current_folder):
    current_year = datetime.now().year  # Année actuelle
    year_folder_ls_command = f'lftp -u {USER},{PASSWD} ftps://{SERVER} -e "set ssl:verify-certificate no; cd {current_year}; ls; bye"'
    year_folder_ls = execute(year_folder_ls_command)  # Exécuter la commande

    # Traiter la sortie et récupérer le dossier le plus récent
    folder_by_date = [int(date) for date in re.findall(r'\b\d{8}\b', year_folder_ls)]
    last_date_folder_from_ftp = max(folder_by_date)

    global new_data_available
    new_data_available = False  # Initialisation du flag

    # Lire la valeur de last_date depuis db.json
    
    last_date = current_folder


    # Comparer la date et télécharger si nécessaire
    if last_date is None or int(last_date) != last_date_folder_from_ftp:
        new_data_available = True
        day_folder_entry_command = f'lftp -u {USER},{PASSWD} ftps://{SERVER} -e "set ssl:verify-certificate no; cd {current_year}; lcd {DOWNLOADS_PATH}; mirror {last_date_folder_from_ftp}; ls; bye"'
        execute(day_folder_entry_command)
    return last_date_folder_from_ftp



def a2_run(data):
    if not os.path.isdir(f'{DOWNLOADS_PATH}processed') :
        os.makedirs(f'{DOWNLOADS_PATH}processed', exist_ok=True)

    list_processed = os.listdir(f'{DOWNLOADS_PATH}processed')
    for file in list_processed :
        os.remove(f'{DOWNLOADS_PATH}processed/{file}')
    
    
    current_folder = data['current_folder']
        
    last_date_folder_from_ftp = ftp_mirror(current_folder)

    time.sleep(1)

    if int(current_folder) < last_date_folder_from_ftp:

        uuid = get_uuid()

        file_treatment(last_date_folder_from_ftp, os.listdir(f'{DOWNLOADS_PATH}{last_date_folder_from_ftp}'), uuid)



        url_post = f"http://127.0.0.1:{APP_PORT}/api/automation/2/update-params"
        current_folder = {"current_folder": last_date_folder_from_ftp}  # Exemple de valeur pour 'current_folder'
        response_post = requests.post(url_post, json={"params": json.dumps(current_folder)})
        print(response_post.text)
