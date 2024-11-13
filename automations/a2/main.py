from datetime import datetime
from dotenv import load_dotenv

import subprocess
import re
import json
import os
import automations.a2.file_treatment as file_treatment


# USER = 'tvanderdonck'       # ftp login
# PASSWD = 'eZN7Rqd85L9q7h'   # ftp passwd
# SERVER = '13.81.52.18'      # ftp host
# TO ADD : DELETE OLDEST FILE
load_dotenv()

USER = os.getenv('FTP_USER')
PASSWD = os.getenv('FTP_PASSWD')
SERVER = os.getenv('FTP_SERVER')



#       *** Partie 1 - Récupérer les xlsx sur le serveur ftp ***


# Obtenir la date actuelle
current_year = datetime.now().year  # set current year 
current_date = f"{datetime.now().year}{datetime.now().month:02}{datetime.now().day:02}" # set current date

def execute(command): #function to execute command with subprocess
    try:
        result = subprocess.run(
            command, 
            shell=True,
            capture_output=True,
            text=True,
            timeout=10  # Ajout d'un timeout pour éviter les blocages
        )
        return result.stdout


    except subprocess.TimeoutExpired:
        print("La commande a pris trop de temps et a été arrêtée.")
        return "Error"


# Construction de la commande avec lftp afin d'aller dans le dossier de la date actuelle (ex:2024/)
year_folder_ls_command = f'lftp -u {USER},{PASSWD} ftps://{SERVER} -e "set ssl:verify-certificate no; cd {current_year}; ls; bye"'
year_folder_ls = execute(year_folder_ls_command) #executer la commande


#Traiter la sortie et récupérer le dossier le plus récent
folder_by_date = [int(date) for date in re.findall(r'\b\d{8}\b', year_folder_ls)]

last_date_folder = max(folder_by_date)


new_data_available = False # flag initilized
with open('save.json', 'r') as file: # open the json fileto check the date of the last folder treated
    try:
        data = json.load(file)
        if int(data.get("lastdate", 0)) != last_date_folder:
            new_data_available = True
            day_folder_entry_command = f'lftp -u {USER},{PASSWD} ftps://{SERVER} -e "set ssl:verify-certificate no; cd {current_year}; lcd upload/ftp_downloads; mirror {last_date_folder}; ls; bye"'
            execute(day_folder_entry_command)
            
            # Réouverture du fichier en mode écriture pour sauvegarder la nouvelle valeur
            with open('save.json', 'w') as file_write:
                json.dump({"lastdate": last_date_folder}, file_write, indent=6)
        else : 
            print("Téléchargement déjà à jour.")

    except (json.JSONDecodeError, FileNotFoundError): 
        # Créer le fichier si inexistant ou s'il est mal formaté
        with open('save.json', 'w') as file_write:
            json.dump({"lastdate": last_date_folder}, file_write, indent=6)



#       *** Partie 2 - Traitement des PDF 1 à 1 ***

file_treatment.file_treatment(last_date_folder, os.listdir(f'upload/ftp_downloads/{last_date_folder}')) if new_data_available    else None


#       *** Partie 3 - Envoie des Feuil2 à CGI comptable ***
