import enum

from flask import current_app
from itsdangerous import Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class AccessRight(str, enum.Enum):
    AUTHORIZED = 'authorized'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

class Key(db.Model):
    __tablename__ = 'keys'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)

    password_hash = db.Column(db.String(256), nullable=False)
    access_right = db.Column(db.Enum(AccessRight), nullable=False, default=AccessRight.AUTHORIZED)

    is_approved = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, login, access_right, is_approved=False):
        self.login = login
        self.access_right = access_right
        self.is_approved = is_approved

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        """Генерує токен для скидання пароля, дійсний 1800 сек (30 хв)."""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'key_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Перевіряє токен. Повертає Key, якщо токен валідний, інакше None."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            key_id = data.get('key_id')
        except Exception:
            return None
        return Key.query.get(key_id)