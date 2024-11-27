from enum import auto
from flask import Flask, render_template, request, redirect, session, send_file, url_for, jsonify
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

# Configuration pour APScheduler
class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

app.secret_key = "une longue phrase qui sert à je ne sais pas quoi"
PASSWORD = "presence123*"


with open('db.json', 'r') as file:
        db_data = json.load(file)
        automations = db_data.get('automations')


# Route pour afficher la page admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Charger le fichier JSON
    with open('db.json', 'r') as f:
        data = json.load(f)

    if request.method == 'POST':
        # Récupérer les données modifiées depuis le formulaire
        updated_data = request.form.get('updated_data')
        
        try:
            # Sauvegarder les nouvelles données dans le fichier JSON
            with open('db.json', 'w') as f:
                json.dump(json.loads(updated_data), f, indent=4)
            return jsonify({"success": True, "message": "Données sauvegardées avec succès."})
        except Exception as e:
            return jsonify({"success": False, "message": f"Erreur : {str(e)}"}), 400

    # Renvoyer la page HTML avec les données actuelles
    return render_template('admin.html', data=json.dumps(data, indent=4))


# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Variable pour stocker les erreurs
    
    # Vérifie si l'utilisateur est déjà authentifié
    if session.get('authenticated'):
        return redirect(url_for('index'))
    
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

@app.route('/logs/<automation_index>')
def get_logs(automation_index):
    try:
        with open('db.json', 'r') as f:
            db_data = json.load(f)
        f.close()
        # Récupérer les logs dynamiquement selon l'ID
        logs = db_data['automations'][int(automation_index)]['logs']
        return jsonify(logs)
    except KeyError:
        return jsonify({"error": "Automation not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
@login_required
def index():

    return render_template('index.html', db=db_data)


@app.route('/a1', methods=['GET', 'POST'])
@login_required
def a1_route():

    return render_template('a1/index.html', current_interval=get_current_interval(automations[0]['id']), automation=automations[0])


@app.route('/a2', methods=['GET'])
@login_required
def a2_route():    
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

@app.route('/test-selenium', methods=['GET'])
def test_selenium():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome  import ChromeDriverManager

    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://www.google.com")
        title = driver.title  # Obtenir le titre de la page
        driver.quit()
        return {"success": True, "title": title}, 200
    except Exception as e:
        return {"success": False, "error": str(e)}, 500




@scheduler.task('interval', id=automations[0]['id'], hours=5, max_instances=1, misfire_grace_time=300)
def a1():
    automat1(automations[0]['last_document_number'])

@scheduler.task('interval', id=automations[1]['id'], hours=12, max_instances=1, misfire_grace_time=300)
def a2():
    automat2()






if __name__ == '__main__':

    # Lancement de l'application Flask
    app.run(debug=False, port=os.getenv("PORT", default=5000) )