from models import db

class Tariff(db.Model):
    __tablename__ = 'tariff'

    id = db.Column(db.Integer, primary_key=True)
    equipment_type_id = db.Column(db.Integer, db.ForeignKey('equipment_type.id'), nullable=False)
    price_per_hour = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Integer, nullable=False)
    weekday_discount = db.Column(db.Integer, nullable=False)

    def __init__(self, equipment_type_id, price_per_hour, price_per_day, weekday_discount):
        self.equipment_type_id = equipment_type_id
        self.price_per_hour = price_per_hour
        self.price_per_day = price_per_day
        self.weekday_discount = weekday_discount