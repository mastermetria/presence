from enum import auto
from flask import Flask, render_template, request, redirect, session, send_file, url_for
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import secrets
import zipfile
import json
import os
import io


from automations.a1.main import run as automat1  # Importation des scripts d'automatisation
from automations.a2.main import run as automat2  # Importation des scripts d'automatisation
from automations.test.main import run as test


# Configuration pour APScheduler
class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

app.secret_key = secrets.token_hex(16)
PASSWORD = "test"


with open('db.json', 'r') as file:
        db_data = json.load(file)
        automations = db_data.get('automations')

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Variable pour stocker les erreurs
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            error = "Mot de passe incorrect !"  # Définit le message d'erreur
    return render_template('login/index.html', error=error, db_data=db_data)

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

# Décorateur pour protéger les pages
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # Nécessaire pour éviter des problèmes avec Flask
    return wrapper


def get_current_interval(id):
    job = scheduler.get_job(id)
    current_interval_seconds = job.trigger.interval.total_seconds() if job else None
    current_interval_hours = current_interval_seconds / 3600 if current_interval_seconds else None

    return current_interval_hours



@app.route('/')
@login_required
def index():

    return render_template('index.html', db=db_data)


@app.route('/a1', methods=['GET', 'POST'])
@login_required
def a1_route():

    a1_db = db_data.get('automations', [])[0]

    automat1(a1_db['last_document_number'])

    pdf_list = os.listdir('automations/a1/downloads')

    return render_template('a1/index.html', db=db_data)


@app.route('/a2', methods=['GET'])
@login_required
def a2_route():    
    
    # Liste des fichiers dans le répertoire spécifié
    try :
        excel_list = os.listdir('automations/a2/downloads/processed')
    except : 
        excel_list = []
    return render_template('a2/index.html', automation=automations[1], current_interval=get_current_interval(automations[1]['id']), excel_list=excel_list)


@app.route('/a2/download', methods=['GET'])
@login_required
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
@login_required
def test_route():


    return render_template('test/index.html', current_interval=get_current_interval(automations[2]['id']), automation=automations[2])




@scheduler.task('interval', id=automations[0]['id'], hours=12)
def a1():
    automat1()

@scheduler.task('interval', id=automations[1]['id'], hours=12)
def a2():
    automat2()

@scheduler.task('interval', id=automations[2]['id'], seconds=10)
def my_task():
    test()



if __name__ == '__main__':

    # Lancement de l'application Flask
    app.run(debug=True)