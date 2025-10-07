from models import db

class Rental(db.Model):
    __tablename__ = 'rental'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref='rentals')
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    rental_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    rental_type = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)

    def __init__(self, client_id, employee_id, rental_date, start_time, end_time, rental_type, total_price):
        self.client_id = client_id
        self.employee_id = employee_id
        self.rental_date = rental_date
        self.start_time = start_time
        self.end_time = end_time
        self.rental_type = rental_type
        self.total_price = total_price