import json
import sqlite3

def initialize_database():
    # Connexion à SQLite
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Création de la table des informations du cabinet
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cabinet_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            created_at TEXT
        )
    ''')

    # Création de la table des automatisations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS automations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT,
            status TEXT,
            time_saved REAL,
            last_document_number TEXT,
            data TEXT -- Stockage des données spécifiques aux automatisations
        )
    ''')

    # Création de la table des logs des automatisations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS automation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            automation_id INTEGER NOT NULL,
            log TEXT,
            FOREIGN KEY (automation_id) REFERENCES automations (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def insert_data_from_json(json_file):
    # Charger les données JSON
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Connexion à SQLite
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insérer les données du cabinet
    cabinet_info = data['cabinet_info']
    cursor.execute('''
        INSERT INTO cabinet_info (name, address, phone, email, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        cabinet_info['name'],
        cabinet_info['address'],
        cabinet_info['contact']['phone'],
        cabinet_info['contact']['email'],
        cabinet_info['created_at']
    ))
    conn.commit()

    # Insérer les automatisations et leurs logs
    for automation in data['automations']:
        # Insérer l'automatisation
        cursor.execute('''
            INSERT INTO automations (name, description, created_at, status, time_saved, last_document_number, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            automation['name'],
            automation['description'],
            automation['created_at'],
            automation['status'],
            automation.get('time_saved', None),
            automation.get('last_document_number', None),
            json.dumps({k: v for k, v in automation.items() if k not in ['id', 'index', 'logs']})  # Ajouter tout sauf id, index et logs
        ))
        automation_id = cursor.lastrowid

        # Insérer les logs
        for log in automation.get('logs', []):
            cursor.execute('''
                INSERT INTO automation_logs (automation_id, log)
                VALUES (?, ?)
            ''', (automation_id, log))

    conn.commit()
    conn.close()
    print("Data inserted successfully from db.json.")

# Initialiser la base de données
initialize_database()

# Insérer les données depuis db.json
insert_data_from_json('db.json')
