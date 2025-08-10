from models import db
from werkzeug.security import generate_password_hash, check_password_hash

class Key(db.Model):
    __tablename__ = 'keys'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    access_right = db.Column(db.String(100), nullable=False)

    def __init__(self, login, password, access_right):
        self.login = login
        self.password = password
        self.access_right = access_right

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)