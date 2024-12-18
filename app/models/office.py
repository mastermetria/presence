from . import db

class Office(db.Model):
    __tablename__ = 'offices'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<Office {self.name}>"