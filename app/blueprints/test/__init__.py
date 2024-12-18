from flask import Blueprint, render_template
from models import Automation
from automations.a1.main import a1_run
from automations.a2.main import a2_run
from automations.test.main import test_run
from extensions import timer
from dotenv import load_dotenv
import requests
import ast
import os

load_dotenv()
APP_PORT = os.getenv('APP_PORT')

test_bp = Blueprint('test', __name__, url_prefix='/test')

@test_bp.route('/')
def home():
    total_time_saved = timer.get_total_time_saved()
    creation_date = timer.get_creation_date()
    all_stat = timer.get_all_stats()
    return render_template('test/test.html', total_time_saved=total_time_saved, creation_date=creation_date, all_stat=all_stat)


@test_bp.route('/test')
def test():

    test_run()
    return 'OK'


@test_bp.route('/a1')
def a1():
    response = requests.get(F"http://localhost:{APP_PORT}/api/automation/1")
    data = response.json()  # Convertir la réponse JSON en dict
    # Vérifier si 'params' est une chaîne ou un dict
    params = data['params']

    if isinstance(params, str):  # Si c'est une chaîne, la convertir en dict
        params = ast.literal_eval(params)
    a1_run(params['last_document_number'])
    return 'OK'

@test_bp.route('/a2')
def a2():
    response = requests.get(F"http://localhost:{APP_PORT}/api/automation/2")
    data = response.json()  # Convertir la réponse JSON en dict

    params = data['params']
    if isinstance(params, str):  # Si c'est une chaîne, la convertir en dict
        params = ast.literal_eval(params)    
    a2_run(params)
    return 'OK'