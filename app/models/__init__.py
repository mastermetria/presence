from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importer les modèles pour les enregistrer dans SQLAlchemy
from .office import Office
from .automation import Automation
from .log import Log