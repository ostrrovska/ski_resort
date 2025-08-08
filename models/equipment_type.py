from models import db

class EquipmentType(db.Model):
    __tablename__ = 'equipment_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

    def __init__(self, name, description):
        self.name = name
        self.description = description