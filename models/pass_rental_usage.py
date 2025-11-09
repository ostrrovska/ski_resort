from models import db


class PassRentalUsage(db.Model):
    __tablename__ = 'pass_rental_usage'

    pass_id = db.Column(db.Integer, db.ForeignKey('pass.id'), primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.id'), primary_key=True)

    hours_deducted = db.Column(db.Float, nullable=False)

    pass_usage = db.relationship('Pass', backref='rental_usages')
    rental = db.relationship('Rental', backref='pass_usage')

    __table_args__ = (
        db.PrimaryKeyConstraint('pass_id', 'rental_id'),
    )

    def __init__(self, pass_id, rental_id, hours_deducted):
        self.pass_id = pass_id
        self.rental_id = rental_id
        self.hours_deducted = hours_deducted