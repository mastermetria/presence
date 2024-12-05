from . import db

class Automation(db.Model):
    __tablename__ = 'automations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrémentation
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255), nullable=True)
    time_saved = db.Column(db.Float, nullable=True)
    params = db.Column(db.JSON, nullable=True)  # Champ générique pour données spécifiques

    logs = db.relationship('Log', backref='automation', lazy=True)
    