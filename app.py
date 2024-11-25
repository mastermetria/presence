from enum import auto
from flask import Flask, render_template, request, redirect, jsonify, send_file
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import io
import zipfile
import json
import threading
import os


from automations.a1.main import run as automat1  # Importation des scripts d'automatisation
from automations.a2.main import run as automat2  # Importation des scripts d'automatisation

# Configuration pour APScheduler
class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

with open('db.json', 'r') as file:
        db_data = json.load(file)
        automations = db_data.get('automations')

@app.route('/')
def index():

    return render_template('index.html', db=db_data)


@app.route('/a1', methods=['GET', 'POST'])
def a1_route():

    a1_db = db_data.get('automations', [])[0]

    automat1(a1_db['last_document_number'])

    pdf_list = os.listdir('automations/a1/downloads')

    return render_template('a1/index.html', db=db_data)


@app.route('/a2', methods=['GET'])
def a2_route():    
    
    #automat2()

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


@app.route('/test', methods=['GET', 'POST'])
def test():
    job = scheduler.get_job(automations[2]['id'])
    current_interval_seconds = job.trigger.interval.total_seconds() if job else None
    current_interval_hours = current_interval_seconds / 3600 if current_interval_seconds else None

    return render_template('test/index.html', current_interval=current_interval_hours, automation=automations[2])



@scheduler.task('interval', id=automations[2]['id'], hours=12)
def my_task():
    print("Tâche exécutée toutes les 12 secondes.")

@scheduler.task('interval', id=automations[0]['id'], hours=12)
def a1():
    automat1()

@scheduler.task('interval', id=automations[1]['id'], hours=12)
def a1():
    automat2()



if __name__ == '__main__':

    # Lancement de l'application Flask
    app.run(debug=True)