from models import db

class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee = db.relationship('Employee', backref='schedules')
    work_date = db.Column(db.Date, nullable=False)
    shift_start = db.Column(db.Time, nullable=False)
    shift_end = db.Column(db.Time, nullable=False)

    def __init__(self, employee_id, work_date, shift_start, shift_end):
        self.employee_id = employee_id
        self.work_date = work_date
        self.shift_start = shift_start
        self.shift_end = shift_end