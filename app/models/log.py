from . import db

class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(255), nullable=False)

    automation_id = db.Column(db.String(10), db.ForeignKey('automations.id'), nullable=False)

    def __repr__(self):
        return f"<Log {self.timestamp} - {self.message}>"