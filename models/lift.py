from models import db

class Lift(db.Model):
    __tablename__ = 'lift'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    height = db.Column(db.Integer, nullable=False)

    def __init__(self, name, height):
        self.name = name
        self.height = height
