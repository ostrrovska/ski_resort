from . import db


class SavedView(db.Model):
    __tablename__ = 'saved_view'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

    client = db.relationship('Client', backref='saved_views')

    def __init__(self, name, url, client_id):
        self.name = name
        self.url = url
        self.client_id = client_id