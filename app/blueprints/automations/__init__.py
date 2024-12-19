from json import load
from flask import Blueprint, render_template, current_app

from extensions import scheduler, timer
from models import Automation

from dotenv import load_dotenv
import os
import ast
import requests

from automations.a1.main import a1_run
from automations.a2.main import a2_run

load_dotenv()
APP_PORT = os.getenv('APP_PORT')

automation_bp = Blueprint('automation', __name__, url_prefix='/automations')


# Route pour la page d'accueil
@automation_bp.route('/home', methods=['GET'])
def home():
    automations = Automation.query.all()
    total_earned_time = timer.get_total_time_saved()
    created_at = timer.get_creation_date()
    return render_template('automations/home.html',timer=timer, total_earned_time=total_earned_time, automations=automations, created_at=created_at)


# Route pour A1
@automation_bp.route('/a1', methods=['GET', 'POST'])
def a1_route():

    automation = Automation.query.get(1)  # Remplace 1 par l'ID correct
    job = scheduler.get_job(automation.id)
    a1_timer = timer.get_function_stats('add_document_in_dext')
    return render_template('automations/auto1.html', timer=a1_timer, automation=automation)


# Route pour A2
@automation_bp.route('/a2', methods=['GET'])
def a2_route():
    try:
        excel_list = os.listdir('automations/a2/downloads/processed')
    except FileNotFoundError:
        excel_list = []
    automation = Automation.query.get(2)  # Remplace 2 par l'ID correct
    a2_timer = timer.get_function_stats('file_treatment')

    return render_template('automations/auto2.html', timer=a2_timer, excel_list=excel_list, automation=automation)


# Tâches programmées
@scheduler.task('interval', id='1', hours=100, max_instances=1, misfire_grace_time=300)
def a1_task():
    response = requests.get(F"http://localhost:{APP_PORT}/api/automation/1")
    data = response.json()  # Convertir la réponse JSON en dict
    # Vérifier si 'params' est une chaîne ou un dict
    params = data['params']

    if isinstance(params, str):  # Si c'est une chaîne, la convertir en dict
        params = ast.literal_eval(params)
    a1_run(params['last_document_number'])

@scheduler.task('interval', id='2', hours=100, max_instances=1, misfire_grace_time=300)
def a2_task():
    response = requests.get(F"http://localhost:{APP_PORT}/api/automation/2")
    data = response.json()  # Convertir la réponse JSON en dict

    params = data['params']
    if isinstance(params, str):  # Si c'est une chaîne, la convertir en dict
        params = ast.literal_eval(params)    
    a2_run(params)
