from models import db

class LiftUsage(db.Model):
    __tablename__ = 'lift_usage'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref='lift_usage')
    lift_id = db.Column(db.Integer, db.ForeignKey('lift.id'), nullable=False)
    lift = db.relationship('Lift', backref='usage')
    usage_date = db.Column(db.Date, nullable=False)
    usage_time_start = db.Column(db.Time, nullable=False)
    usage_time_end = db.Column(db.Time, nullable=False)

    def __init__(self, client_id, lift_id, usage_date, usage_time_start, usage_time_end):
        self.client_id = client_id
        self.lift_id = lift_id
        self.usage_date = usage_date
        self.usage_time_start = usage_time_start
        self.usage_time_end = usage_time_end