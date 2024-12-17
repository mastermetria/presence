from datetime import datetime

import warnings
import time
from idna import encode
import pandas as pd
import subprocess
import json
import re
import os
from dotenv import load_dotenv
import requests

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

load_dotenv()

USER = os.getenv('A2_FTP_LOGIN')
PASSWD = os.getenv('A2_FTP_PASSWORD')
SERVER = os.getenv('A2_FTP_SERVER')

A2_PATH = './automations/a2/'
DOWNLOADS_PATH = './automations/a2/downloads/'

feuil3_dict = {
    "CDE": ("604020000", "467100000"),
    "CROIX-ROUGE": ("604021000", "467110000"),
    "PASTEUR": ("604022000", "467120000"),
    "MDM": ("604023000", "467130000"),
    "WWF": ("604024000", "467140000"),
    "UNHCR": ("604025000", "467150000"),
    "ACTION FAIM": ("604026000", "467160000"),
    "UNICEF": ("604027000", "467170000"),
    "QUITOQUE": ("604028000", "467180000"),
    "SOLIDARITES": ("604029000", "467190000"),
    "CARE": ("604030000", "467200000"),
    "ACTIONFAIM": ("604031000", "467210000"),
    "EFS": ("604032000", "467220000"),
}
folder_dict = {
    "APEX": ["APEX2", "TEST"],
    "DAY 1": ["DAY1", "TEST"],
    "DLG CORPORATION": ["DLGCORP", "TEST"],
    "EMPOWER CORP": ["EMPOWER", "TEST"],
    "EMPOWER": ["EMPOWER", "TEST"],
    "GHEPARDO MARKETING": ["GHEPARDO", "TEST"],
    "GHEPARDO": ["GHEPARDO", "TEST"],
    "GRAVITY MARKETING": ["GRAVITY", "TEST"],
    "KYS": ["KYS", "TEST"],
    "REVIVAL": ["REVIVAL", "TEST"],
    "REWARD PARTNERS": ["REWARDPAR", "TEST"],
    "SLS DIVISION": ["SLSDIVISIO", "TEST"],
    "VICTORY MARKETING": ["VICTORYMAR", "TEST"]
}
def get_uuid():

    url = "https://isuite.antaris.fr/CNX/api/v1/authentification"

    payload = json.dumps({
    "Identifiant": "OPPY",
    "MotDePasse": "OPPY123*"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json().get('UUID')

def col_to_num(col):
    """
    Convertit une référence de colonne Excel (base 26) en nombre entier (base 10).

    """
    result = 0
    for i, char in enumerate(reversed(col)):
        result += (ord(char.upper()) - ord('A') + 1) * (26 ** i)
    return result - 1

def connect_to_folder(uuid, mc_name):

    url = "https://isuite.antaris.fr/CNX/api/v1/sessions/dossier"

    payload = json.dumps(mc_name)
    headers = {
    'accept': 'text/plain',
    'UUID': uuid,
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    pass

def create_provider_account(uuid, code, lib):

    url = "https://isuite.antaris.fr/CNX/api/v1/compta/comptes/fournisseur"

    payload = json.dumps({
    "Code": code,
    "Lib": lib,
    "Let": "",
    "CptHTAssocie": "",
    "CptCptCol": ""
    })
    headers = {
    'accept': 'text/plain',
    'UUID': uuid,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(f"Création compte fournisseur : {response.text}")

def create_account(uuid, code, lib):
    url = "https://isuite.antaris.fr/CNX/api/v1/compta/comptes/generaux"

    payload = json.dumps({
    "Code": code,
    "Lib": lib,
    "Let": "",
    "CodeTva": "",
    "CptCptCol": ""
    })
    headers = {
    'accept': 'text/plain',
    'UUID': uuid,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(f"Création compte général : {response.text}")

def verif_campaign_name(campaign_name, uuid):
    """
    Ajoute une nouvelle entrée au dictionnaire feuil3_dict en respectant la suite logique des valeurs.

    :param feuil3_dict: Le dictionnaire existant.
    :param campaign_name: Le nom de la campagne à ajouter.
    :return: La liste des valeurs ajoutées.
    """
    # Obtenir les dernières valeurs du dictionnaire
    if not campaign_name in feuil3_dict :
        last_values = list(feuil3_dict.values())[-1]
        last_value_1 = int(last_values[0])
        last_value_2 = int(last_values[1])

        # Calculer les nouvelles valeurs en incrémentant de 1
        new_value_1 = str(last_value_1 + 1000)
        new_value_2 = str(last_value_2 + 10000)
        # Ajouter la nouvelle entrée au dictionnaire
        feuil3_dict[campaign_name] = (new_value_1, new_value_2)

        create_account(uuid, new_value_1, campaign_name)
        create_account(uuid, new_value_2, campaign_name)
    else : 
        create_account(uuid, feuil3_dict[campaign_name][1], campaign_name)
        create_account(uuid, feuil3_dict[campaign_name][0], campaign_name)

    return feuil3_dict[campaign_name]

def send_data(uuid, data):
    url = "https://isuite.antaris.fr/CNX/api/v1/compta/ecriture"

    payload = json.dumps(data)
    headers = {
    'accept': 'text/plain',
    'UUID': uuid,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(f"Envoie des écritures : {response.text}")


def file_treatment(max_nb, file_list, uuid):
    
    for file in file_list[-2:-1]:
        print(f'file name : {file}')
        df = pd.read_excel(f'{DOWNLOADS_PATH}{max_nb}/{file}',sheet_name='BA Payments New', header=None)

        date = df.iloc[0, 2].strftime("%m/%d/%Y")
        mc_name = df.iloc[2, 2].strip().upper()
        campaign_type = df.iloc[3,2].strip().upper()
        campaign_name = df.iloc[4,2].strip().upper()
        print(date, mc_name, campaign_type, campaign_name)

        df_filtered = df.iloc[17:]
        df_filtered = df_filtered[df_filtered.iloc[:, 3].notna() & (df_filtered.iloc[:, 3].astype(str).str.strip() != "")]
        
        data = []

        if not df_filtered.empty :
            
            connect_to_folder(uuid, mc_name)
            verif_campaign_name(campaign_name, uuid)

            body = {
                "Journal": folder_dict[mc_name][1],
                "Mois": int(date.split('/')[0]),
                "Annee": int(date.split('/')[2]),
                "ReferenceGed": "",
                "LignesEcriture": data,
                "Periode": {
                    "DateDebut": "2024-12-03T07:17:52.833Z",
                    "DateFin": "2024-12-03T07:17:52.833Z"
                    }
            }

            if campaign_type == 'FUNDRAISING':
                provision_line1= {
                    "Jour": int(date.split('/')[1]),
                    "NumeroPiece": "",
                    "NumeroFacture": "",
                    "Compte": feuil3_dict[campaign_name][1],
                    "CodeTVA": "",
                    "Libelle": "PROVISION RETENUE 30%",
                    "Credit": df.iloc[15, col_to_num('AJ')] -df.iloc[15, col_to_num('AH')] if df.iloc[15, col_to_num('AJ')]> 0 else 0,
                    "Debit": -df.iloc[15, col_to_num('AJ')] -df.iloc[15, col_to_num('AH')] if df.iloc[15, col_to_num('AJ')]< 0 else 0,
                    "ModeReglement": "",
                    "ReferenceGed": ""
                    }
                provision_line2= {
                    "Jour": int(date.split('/')[1]),
                    "NumeroPiece": "",
                    "NumeroFacture": "",
                    "Compte": feuil3_dict[campaign_name][0],
                    "CodeTVA": "",
                    "Libelle": "PROVISION RETENUE 30%",
                    "Credit": -df.iloc[15, col_to_num('AJ')] -df.iloc[15, col_to_num('AH')] if df.iloc[15, col_to_num('AJ')]< 0 else 0,
                    "Debit": df.iloc[15, col_to_num('AJ')] -df.iloc[15, col_to_num('AH')] if df.iloc[15, col_to_num('AJ')]> 0 else 0,
                    "ModeReglement": "",
                    "ReferenceGed": ""
                    }
                data.extend([provision_line1, provision_line2])
                send_data(uuid, body)
                data.clear()
            
            for _, row in df_filtered.iterrows():

                create_provider_account(uuid, f'F000{row.iloc[col_to_num('C')]}', row.iloc[col_to_num('D')])

                if campaign_type == 'FUNDRAISING':
                    fundraising_line1= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": feuil3_dict[campaign_name][0],
                        "CodeTVA": "",
                        "Libelle": f"{row.iloc[col_to_num('C')]} {row.iloc[col_to_num('D')]} commis. brutes",
                        "Credit": 0,
                        "Debit": (0 if isinstance(row.iloc[col_to_num('AC')], str) or pd.isna(row.iloc[col_to_num('AC')]) else round(row.iloc[col_to_num('AC')], 2)) + \
                                (0 if isinstance(row.iloc[col_to_num('AK')], str)  or pd.isna(row.iloc[col_to_num('AK')]) else round(row.iloc[col_to_num('AK')], 2)) + \
                                (0 if isinstance(row.iloc[col_to_num('AL')], str)  or pd.isna(row.iloc[col_to_num('AL')]) else round(row.iloc[col_to_num('AL')], 2)),
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    fundraising_line2= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": feuil3_dict[campaign_name][1],
                        "CodeTVA": "",
                        "Libelle": f"{row.iloc[col_to_num('C')]} {row.iloc[col_to_num('D')]} commis. brutes",
                        "Credit": round(-row.iloc[col_to_num('AJ')] -row.iloc[col_to_num('AH')], 2) if row.iloc[col_to_num('AJ')]< 0 else 0,
                        "Debit": round(row.iloc[col_to_num('AJ')] -row.iloc[col_to_num('AH')], 2) if row.iloc[col_to_num('AJ')]> 0  else 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    fundraising_line3= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": "437600000",
                        "CodeTVA": "",
                        "Libelle": f"{row.iloc[col_to_num('C')]} {row.iloc[col_to_num('D')]} commis. brutes",
                        "Credit": 0 if pd.isna(row.iloc[col_to_num('AO')]) else round(-row.iloc[col_to_num('AO')], 2),
                        "Debit": 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    fundraising_line4= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": "791000000",
                        "CodeTVA": "",
                        "Libelle": f"{row.iloc[col_to_num('C')]} {row.iloc[col_to_num('D')]} commis. brutes",
                        "Credit": 0 if pd.isna(row.iloc[col_to_num('AP')]) else round(-row.iloc[col_to_num('AP')]/1.2, 2),
                        "Debit": 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    fundraising_line5= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": "445717000",
                        "CodeTVA": "",
                        "Libelle": f"{row.iloc[col_to_num('C')]} {row.iloc[col_to_num('D')]} commis. brutes",
                        "Credit": 0 if pd.isna(row.iloc[col_to_num('AP')]) else round(-row.iloc[col_to_num('AP')]/1.2*0.2, 2),
                        "Debit": 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    fundraising_line6= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": f"F000{row.iloc[col_to_num('C')]}",
                        "CodeTVA": "",
                        "Libelle": f"{row.iloc[col_to_num('C')]} {row.iloc[col_to_num('D')]} commis. brutes",
                        "Credit": 0 if pd.isna(row.iloc[col_to_num('AS')]) else round(row.iloc[col_to_num('AS')], 2),
                        "Debit": 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    
                    data.extend([fundraising_line1, fundraising_line2, fundraising_line3, fundraising_line4, fundraising_line5, fundraising_line6])
                    send_data(uuid, body)
                    data.clear()

                elif campaign_type == 'COMMERCIAL':
                    commercial_line1= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": feuil3_dict[campaign_name][0],
                        "CodeTVA": "",
                        "Libelle": f"{row[col_to_num('C')]} {row[col_to_num('D')]} commis. brutes",
                        "Credit": 0,
                        "Debit": (0 if isinstance(row.iloc[col_to_num('AH')], str) or pd.isna(row.iloc[col_to_num('AH')]) else round(row.iloc[col_to_num('AH')], 2)) + \
                                (0 if isinstance(row.iloc[col_to_num('AI')], str)  or pd.isna(row.iloc[col_to_num('AI')]) else round(row.iloc[col_to_num('AI')], 2)) + \
                                (0 if isinstance(row.iloc[col_to_num('AJ')], str)  or pd.isna(row.iloc[col_to_num('AJ')]) else round(row.iloc[col_to_num('AJ')], 2)),
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    commercial_line2= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": "437600000",
                        "CodeTVA": "",
                        "Libelle": f"{row[col_to_num('C')]} {row[col_to_num('D')]} commis. brutes",
                        "Credit":  0 if pd.isna(row.iloc[col_to_num('AM')]) else round(-row.iloc[col_to_num('AM')], 2),
                        "Debit": 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    commercial_line3= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": "791000000",
                        "CodeTVA": "",
                        "Libelle": f"{row[col_to_num('C')]} {row[col_to_num('D')]} commis. brutes",
                        "Credit": 0 if pd.isna(row.iloc[col_to_num('AN')]) else round(-row.iloc[col_to_num('AP')]/1.2, 2),
                        "Debit": 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    commercial_line4= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": "445717000",
                        "CodeTVA": "",
                        "Libelle": f"{row[col_to_num('C')]} {row[col_to_num('D')]} commis. brutes",
                        "Credit": 0 if pd.isna(row.iloc[col_to_num('AN')]) else round(-row.iloc[col_to_num('AP')]/1.2*0.2, 2),
                        "Debit": 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    commercial_line5= {
                        "Jour": int(date.split('/')[1]),
                        "NumeroPiece": "",
                        "NumeroFacture": "",
                        "Compte": f"F000{row.iloc[col_to_num('C')]}",
                        "CodeTVA": "",
                        "Libelle": f"{row[col_to_num('C')]} {row[col_to_num('D')]} commis. brutes",
                        "Credit": 0 if pd.isna(row.iloc[col_to_num('AQ')]) else round(row.iloc[col_to_num('AQ')], 2),
                        "Debit": 0,
                        "ModeReglement": "",
                        "ReferenceGed": ""
                        }
                    data.extend([commercial_line1, commercial_line2, commercial_line3, commercial_line4, commercial_line5])
                    send_data(uuid, body)
                    data.clear()

        else : 
            print("fichier pas a traiter")



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


def ftp_mirror(last_date):
    current_year = datetime.now().year  # Année actuelle
    year_folder_ls_command = f'lftp -u {USER},{PASSWD} ftps://{SERVER} -e "set ssl:verify-certificate no; cd {current_year}; ls; bye"'
    year_folder_ls = execute(year_folder_ls_command)  # Exécuter la commande

    # Traiter la sortie et récupérer le dossier le plus récent
    folder_by_date = [int(date) for date in re.findall(r'\b\d{8}\b', year_folder_ls)]
    last_date_folder = max(folder_by_date)




    # Comparer la date et télécharger si nécessaire
    if last_date is None or int(last_date) != last_date_folder:
        new_data_available = True
        day_folder_entry_command = f'lftp -u {USER},{PASSWD} ftps://{SERVER} -e "set ssl:verify-certificate no; cd {current_year}; lcd {DOWNLOADS_PATH}; mirror {last_date_folder}; ls; bye"'
        execute(day_folder_entry_command)

    return last_date_folder

def a2_run(params):
    last_date_saved = params['current_folder']
    last_date_from_ftp = ftp_mirror(last_date_saved)
    time.sleep(1)

    uuid = get_uuid()
    if last_date_saved is None or int(last_date_saved) < last_date_from_ftp :
        file_treatment(last_date_from_ftp, os.listdir(f'{DOWNLOADS_PATH}{last_date_from_ftp}'), uuid)

        url = "http://127.0.0.1:5000/api/automation/2/update-params"

        payload = json.dumps({
        "params": {
            "current_folder": last_date_from_ftp,
            "feuil3_dict": feuil3_dict
        }
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
    else : 
        print("up to date")