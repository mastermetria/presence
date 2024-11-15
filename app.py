from flask import Flask, render_template, request, redirect, jsonify, send_file
import io
import zipfile
from automations.a1.main import run
from apscheduler.schedulers.background import BackgroundScheduler
from automations.a1.main import run  # Importation des scripts d'automatisation
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

    if request.method == 'POST':
        user_input = request.form.get('content')

        if user_input is None:
            # Retourne un message d'erreur si aucun input n'est reçu
            return "No input received", 400

        thread = threading.Thread(target=run, args=(user_input,))
        thread.start()

        # Retourne toujours une réponse en chaîne de caractères
        return redirect('/a1')
    else:
        pdf_list = os.listdir('automations/a1/downloads')
        return render_template('a1/interface.html', db=db_data)


@app.route('/a1/get_pdfs')
def get_pdfs():
    # Obtenir la liste des fichiers PDF dans le dossier
    pdf_files = [f for f in os.listdir(
        'automations/a1/downloads') if f.endswith('.pdf')]
    return jsonify(pdf_files)


DOWNLOAD_FOLDER = "automations/a1/downloads"


@app.route('/a1/get_folder')
def get_folder():
    # Crée un objet BytesIO pour stocker le fichier ZIP en mémoire
    zip_stream = io.BytesIO()

    # Création du fichier ZIP en mémoire
    with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
            for file in files:
                # Ajoute chaque fichier du dossier dans le ZIP
                zipf.write(os.path.join(root, file), os.path.relpath(
                    os.path.join(root, file), DOWNLOAD_FOLDER))

    # Repositionner le pointeur au début du BytesIO pour le téléchargement
    zip_stream.seek(0)

    # Retourner le fichier ZIP en tant que fichier téléchargeable
    return send_file(
        zip_stream,
        mimetype='application/zip',
        as_attachment=True,
        download_name='downloads.zip'
    )


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
