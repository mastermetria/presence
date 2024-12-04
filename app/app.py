from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from models import db

from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.automations import automation_bp, scheduler
from blueprints.api import api_bp

from models import Automation

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

# Initialiser APScheduler
scheduler.init_app(app)
scheduler.start()

# Secret key for session
app.secret_key = "une longue phrase qui sert à je ne sais pas quoi"

# Enregistrer les Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(automation_bp)
app.register_blueprint(api_bp)



@app.route("/", methods=['GET'])
def index():
    return redirect(url_for('automation.home'))

# Fonction pour recharger les données
def refresh_automations():
    with app.app_context():  # Assurer que le contexte est actif
        automations = Automation.query.all()
        app.config['AUTOMATIONS'] = automations
        print(f"{len(automations)} automatisations rechargées.")

# Planifier la tâche de rechargement automatique
@scheduler.task('interval', id='refresh_task', seconds=300)  # Exécute toutes les 5 minutes
def scheduled_refresh():
    refresh_automations()

# Initialisation des données au démarrage de l'application
with app.app_context():
    app.config['AUTOMATIONS'] = Automation.query.all()



if __name__ == '__main__':
    app.run(debug=False, port=5000)
