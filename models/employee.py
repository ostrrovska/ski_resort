from models import db

class Employee(db.Model):
    __tablename__ = 'employee'

    name = db.Column(db.String(100), primary_key=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __init__(self, name, age):
        self.name = name
        self.age = age