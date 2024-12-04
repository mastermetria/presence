from flask import Blueprint, render_template, jsonify
from flask_apscheduler import APScheduler

import os

from models import Automation # Import de ton modèle SQLAlchemy

from automations.a1.main import run as automat1
from automations.a2.main import run as automat2


automation_bp = Blueprint('automation', __name__, url_prefix='/automations')

# Configuration pour APScheduler
scheduler = APScheduler()


# Route pour la page d'accueil
@automation_bp.route('/home', methods=['GET'])
def home():
    automations = Automation.query.all()
    # Exemple de données à afficher
    total_earned_time = 42.5  # Exemple : temps total économisé (calcule dynamiquement selon les automations)
    return render_template('automations/home.html', total_earned_time=total_earned_time, automations=automations)



@automation_bp.route('/a1', methods=['GET', 'POST'])
def a1_route():
    automation = Automation.query.get(1)  # Remplace 1 par l'ID correspondant
    return render_template('automations/auto1.html', time_saved=0, automation=automation)



@automation_bp.route('/a2', methods=['GET'])
def a2_route():
    try:
        excel_list = os.listdir('automations/a2/downloads/processed')
    except:
        excel_list = []
    automation = Automation.query.get(1)  # Remplace 1 par l'ID correspondant
    return render_template('automations/auto2.html', time_saved=0, excel_list=excel_list, automation=automation)



# Tâches programmées
@scheduler.task('interval', id='automation_a1', hours=5, max_instances=1, misfire_grace_time=300)
def a1_task():
    automat1("last_document_number")  # Tu peux ajuster les paramètres ici

@scheduler.task('interval', id='automation_a2', seconds=30, max_instances=1, misfire_grace_time=300)
def a2_task():
    automat2()
