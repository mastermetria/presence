from flask import Flask, render_template, request, redirect, jsonify, send_file
from automations.a1.main import run
from apscheduler.schedulers.background import BackgroundScheduler
from automations.a1.main import run as a1 # Importation des scripts d'automatisation
from automations.a2.main import run as automat2# Importation des scripts d'automatisation

import io
import zipfile
import json
import threading
import os

app = Flask(__name__)


@app.route('/')
def index():
    with open('db.json', 'r') as file:
        db_data = json.load(file)
    return render_template('index.html', db=db_data)


@app.route('/a1', methods=['GET', 'POST'])
def a1():
    with open('db.json', 'r') as file:
        db_data = json.load(file)

    pdf_list = os.listdir('automations/a1/downloads')
    return render_template('a1/interface.html', db=db_data)

@app.route('/a2', methods=['GET'])
def a2():
    with open('db.json', 'r') as file:
            db_data = json.load(file)
    automat2()
    return render_template('a2/index.html', db=db_data)



if __name__ == '__main__':
    app.run(debug=True)


# def a2():
#     pass
# # Configurer et démarrer le planificateur
# scheduler = BackgroundScheduler()
# scheduler.add_job(automated_task, 'interval', hours=12)
# scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)
