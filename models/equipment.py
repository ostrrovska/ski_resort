from models import db

class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('equipment_type.id'), nullable=False)
    type = db.relationship('EquipmentType', backref='equipment')
    model = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, nullable=False)

    def __init__(self, type_id, model, is_available):
        self.type_id = type_id
        self.model = model
        self.is_available = is_available