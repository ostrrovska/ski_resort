from models import db

class Pass(db.Model):
    __tablename__ = 'pass'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref='passes')
    pass_type_id = db.Column(db.Integer, db.ForeignKey('pass_type.id'), nullable=False)
    pass_type = db.relationship('PassType', backref='passes')
    purchase_date = db.Column(db.Date, nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=False)
    remaining_lifts = db.Column(db.Integer, nullable=False)
    remaining_hours = db.Column(db.Integer, nullable=False)

    def __init__(self, client_id, pass_type_id, purchase_date, valid_from, valid_to, remaining_lifts, remaining_hours):
        self.client_id = client_id
        self.pass_type_id = pass_type_id
        self.purchase_date = purchase_date
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.remaining_lifts = remaining_lifts
        self.remaining_hours = remaining_hours