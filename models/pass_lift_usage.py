from models import db

class PassLiftUsage(db.Model):
    __tablename__ = 'pass_lift_usage'

    pass_id = db.Column(db.Integer, db.ForeignKey('pass.id'))
    lift_usage_id = db.Column(db.Integer, db.ForeignKey('lift_usage.id'))
    pass_usage = db.relationship('Pass', backref='lift_usages')
    lift_usage = db.relationship('LiftUsage', backref='pass_usages')

    __table_args__ = (
        db.PrimaryKeyConstraint('pass_id', 'lift_usage_id'),
    )

    def __init__(self, pass_id, lift_usage_id):
        self.pass_id = pass_id
        self.lift_usage_id = lift_usage_id
