from models import db

class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    document_id = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __init__(self, full_name, document_id, date_of_birth, phone_number, email):
        self.full_name = full_name
        self.document_id = document_id
        self.date_of_birth = date_of_birth
        self.phone_number = phone_number
        self.email = email