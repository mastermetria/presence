from flask import Blueprint
from models import Automation
from automations.a1.main import a1_run
from automations.a2.main import a2_run

from dotenv import load_dotenv
import requests
import ast
import os

load_dotenv()
APP_PORT = os.getenv('APP_PORT')

test_bp = Blueprint('test', __name__, url_prefix='/test')


@test_bp.route('/a1')
def a1():
    response = requests.get(F"http://localhost:{APP_PORT}/api/automation/1")
    data = response.json()  # Convertir la réponse JSON en dict
    params = ast.literal_eval(data['params'])
    return 'OK'

@test_bp.route('/a2')
def a2():
    response = requests.get(F"http://localhost:{APP_PORT}/api/automation/2")
    data = response.json()  # Convertir la réponse JSON en dict
    params = ast.literal_eval(data['params'])
    a2_run(params)
    return 'OK'