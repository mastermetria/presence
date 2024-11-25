from flask import Flask, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'  # Remplacez par une clé secrète sécurisée

# Mot de passe défini pour accéder aux pages
PASSWORD = "mon_mot_de_passe"

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        return "Mot de passe incorrect", 401
    return '''
        <form method="post">
            <label for="password">Mot de passe :</label>
            <input type="password" name="password" id="password">
            <button type="submit">Se connecter</button>
        </form>
    '''

# Décorateur pour protéger les pages
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # Nécessaire pour éviter des problèmes avec Flask
    return wrapper

# Route protégée
@app.route('/')
@login_required
def index():
    return "Bienvenue sur la page protégée !"

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
