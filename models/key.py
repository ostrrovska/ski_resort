from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Key(db.Model):
    __tablename__ = 'keys'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)

    password_hash = db.Column(db.String(256), nullable=False)
    access_right = db.Column(db.String(50), nullable=False)

    def __init__(self, login, access_right):
        self.login = login
        self.access_right = access_right

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)