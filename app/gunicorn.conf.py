import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Paramètres de Gunicorn basés sur les variables d'environnement
bind = f"0.0.0.0:{os.getenv('APP_PORT', '5000')}"  # Par défaut, utilise 5000 si APP_PORT n'est pas défini
workers = int(os.getenv('GUNICORN_WORKERS', 1))  # Par défaut, 4 workers
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gevent')  # Par défaut, 'gevent'
timeout = int(os.getenv('GUNICORN_TIMEOUT', 30))  # Par défaut, 30 secondes
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')  # Par défaut, stdout
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')  # Par défaut, stderr
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')  # Par défaut, 'info'