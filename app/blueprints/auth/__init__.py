from flask import Blueprint, render_template, request, redirect, session, url_for

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

PASSWORD = "presence123*"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('authenticated'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            error = "Mot de passe incorrect !"
    return render_template('auth/login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('auth.login'))