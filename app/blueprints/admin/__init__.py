from flask import Blueprint, render_template, request, jsonify
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET', 'POST'])
def admin():
    return render_template('admin/admin.html')

