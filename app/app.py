from flask import Flask, redirect, url_for
from flask_migrate import Migrate

from models import db

from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.automations import automation_bp
from blueprints.api import api_bp
from blueprints.test import test_bp

from extensions import scheduler

from dotenv import load_dotenv
import os


load_dotenv()

DEBUG_MODE = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
APP_PORT = int(os.getenv('APP_PORT', 5000))
DATABASE_URL = os.getenv("DATABASE_URL")

class Config:
    SCHEDULER_API_ENABLED = True
    SECRET_KEY = os.getenv('SECRET_KEY')



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    # Initialiser APScheduler
    scheduler.init_app(app)
    scheduler.start()

    # Enregistrer les Blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(automation_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(test_bp)

    return app


# Initialisation de l'application
app = create_app()

@app.route("/", methods=['GET'])
def index():
    return redirect(url_for('automation.home'))


if __name__ == '__main__':
    print(DATABASE_URL)
    app.run(debug=DEBUG_MODE, port=APP_PORT)
