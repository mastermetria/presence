from enum import auto
from flask import Flask, render_template, request, redirect, jsonify, send_file
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import io
import zipfile
import json
import threading
import os

from automations.a1.main import run as automat1  # Importation des scripts d'automatisation
from automations.a2.main import run as automat2  # Importation des scripts d'automatisation

app = Flask(__name__)

# # Fonction pour exécuter automat2
# def run_automat2():
#     print("Exécution automatique de automat2...")
#     automat2()

# # Initialisation du scheduler
# scheduler = BackgroundScheduler()
# scheduler.start()

# # Ajout d'une tâche planifiée pour exécuter automat2 toutes les 12 heures
# scheduler.add_job(
#     run_automat2,
#     trigger=IntervalTrigger(hours=12),
#     id='automat2_job',
#     replace_existing=True
# )

@app.route('/')
def index():
    with open('db.json', 'r') as file:
        db_data = json.load(file)
    return render_template('index.html', db=db_data)


@app.route('/a1', methods=['GET', 'POST'])
def a1_route():
    with open('db.json', 'r') as file:
        db_data = json.load(file)

    automat1("130-70007551")
    pdf_list = os.listdir('automations/a1/downloads')
    return render_template('a1/index.html', db=db_data)



@app.route('/a2', methods=['GET'])
def a2_route():    
    with open('db.json', 'r') as file:
        db_data = json.load(file)

    automat2()

    # Liste des fichiers dans le répertoire spécifié
    try :
        excel_list = os.listdir('automations/a2/downloads/processed')
    except : 
        excel_list = []
    return render_template('a2/index.html', db=db_data, excel_list=excel_list)


@app.route('/a2/download', methods=['GET'])
def download_folder():
    folder_path = 'automations/a2/downloads/processed'
    zip_filename = 'processed_files.zip'

    # Crée un objet ZIP en mémoire
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, arcname)
    zip_buffer.seek(0)

    # Renvoie le fichier ZIP
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        print("fin")
