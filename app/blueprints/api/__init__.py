from flask import jsonify, Blueprint, request
from db_utils import get_automation_by_id, update_automation_status, update_automation_params
from models import Automation



api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/automations', methods=['GET'])
def get_all_automations():
    """
    Retourne toutes les automatisations.
    """
    automations = Automation.query.all()
    return jsonify([{"id": a.id,
                      "name": a.name, 
                      "description": a.description, 
                      "created_at": a.created_at, 
                      "status": a.status, 
                      "link": a.link, 
                      "time_saved": a.time_saved, 
                      "params": a.params
                      } for a in automations])

@api_bp.route('/automation/<int:automation_id>', methods=['GET'])
def get_automation(automation_id):
    """
    Retourne une automation spécifique par ID.
    """
    automation = get_automation_by_id(automation_id)
    if automation:
        return jsonify({"id": automation.id,
                      "name": automation.name, 
                      "description": automation.description, 
                      "created_at": automation.created_at, 
                      "status": automation.status, 
                      "link": automation.link, 
                      "time_saved": automation.time_saved, 
                      "params": automation.params
                      })
    return jsonify({"error": "Automation not found"}), 404

@api_bp.route('/automation/<int:automation_id>/update-status', methods=['POST'])
def update_status(automation_id):
    """
    Met à jour le statut d'une automation.
    """
    data = request.get_json()
    status = data.get('status')

    if status is None:
        return jsonify({"error": "Missing 'status' field"}), 400

    automation = update_automation_status(automation_id, status)
    if automation:
        return jsonify({"message": f"Automation {automation.id} status updated to {status}"})
    return jsonify({"error": "Automation not found"}), 404


@api_bp.route('/automation/<int:automation_id>/update-params', methods=['POST'])
def update_params(automation_id):
    """
    Met à jour les paramètres d'une automation.
    """
    from models import db  # Assurez-vous de remplacer par le bon module de base de données

    data = request.get_json()
    params = data.get('params')

    if params is None:
        return jsonify({"error": "Missing 'params' field"}), 400

    try:
        # Assurez-vous de récupérer l'objet avec une session active
        automation = db.session.query(Automation).filter_by(id=automation_id).first()

        if not automation:
            return jsonify({"error": "Automation not found"}), 404

        # Mettre à jour les paramètres
        automation.params = params
        db.session.commit()

        return jsonify({"message": f"Automation {automation.id} params updated", "params": params})

    except Exception as e:
        # Gérer les erreurs et assurer une rollback de la session en cas d'échec
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
