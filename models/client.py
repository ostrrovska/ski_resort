from models import db
from werkzeug.security import generate_password_hash, check_password_hash

class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    document_id = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __init__(self, full_name, document_id, date_of_birth, phone_number, email, username):
        self.full_name = full_name
        self.document_id = document_id
        self.date_of_birth = date_of_birth
        self.phone_number = phone_number
        self.email = email
        self.username = username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)