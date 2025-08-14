from models import db

class PassType(db.Model):
    __tablename__ = 'pass_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    limit_lifts = db.Column(db.Integer, nullable=False)
    limit_hours = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self, name, limit_lifts, limit_hours, price):
        self.name = name
        self.limit_lifts = limit_lifts
        self.limit_hours = limit_hours
        self.price = price