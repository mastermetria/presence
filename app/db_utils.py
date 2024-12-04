from models import Automation, db
from flask import current_app

def get_automation_by_id(automation_id):
    """
    Récupère une entrée de la table Automation par son ID.
    """
    with current_app.app_context():  # Utilise le contexte Flask actif
        return Automation.query.get(automation_id)

def update_automation_status(automation_id, status):
    """
    Met à jour le statut d'une entrée de la table Automation.
    """
    with current_app.app_context():  # Utilise le contexte Flask actif
        automation = Automation.query.get(automation_id)
        if automation:
            automation.status = status
            db.session.commit()
            return automation
        return None

def update_automation_params(automation_id, params):
    """
    Met à jour le statut d'une entrée de la table Automation.
    """
    with current_app.app_context():  # Utilise le contexte Flask actif
        automation = Automation.query.get(automation_id)
        if automation:
            automation.params = params
            db.session.commit()
            return automation
        return None
