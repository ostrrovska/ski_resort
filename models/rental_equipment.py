from models import db

class RentalEquipment(db.Model):
    __tablename__ = 'rental_equipment'

    rental_id = db.Column(db.Integer, db.ForeignKey('rental.id'), primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
    rental = db.relationship('Rental', backref='equipment_usages')
    equipment = db.relationship('Equipment', backref='rental_usages')

    __table_args__ = (
        db.PrimaryKeyConstraint('rental_id', 'equipment_id'),
    )

    def __init__(self, rental_id, equipment_id):
        self.rental_id = rental_id
        self.equipment_id = equipment_id