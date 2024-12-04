from flask import Blueprint, render_template, request, jsonify
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET', 'POST'])
def admin():
    # Charger le fichier JSON
    with open('db.json', 'r') as f:
        data = json.load(f)

    if request.method == 'POST':
        # Récupérer les données modifiées depuis le formulaire
        updated_data = request.form.get('updated_data')
        
        try:
            # Sauvegarder les nouvelles données dans le fichier JSON
            with open('db.json', 'w') as f:
                json.dump(json.loads(updated_data), f, indent=4)
            return jsonify({"success": True, "message": "Données sauvegardées avec succès."})
        except Exception as e:
            return jsonify({"success": False, "message": f"Erreur : {str(e)}"}), 400

    return render_template('admin.html', data=json.dumps(data, indent=4))

