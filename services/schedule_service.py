from models.schedule import Schedule, db

class ScheduleService:

    @staticmethod
    def get_all():
        return Schedule.query.all()

    @staticmethod
    def get_by_id(id):
        return Schedule.query.get(id)

    @staticmethod
    def add(employee_id, work_date, shift_start, shift_end):
        new_schedule = Schedule(employee_id, work_date, shift_start, shift_end)
        db.session.add(new_schedule)
        db.session.commit()
        return new_schedule

    @staticmethod
    def update(id, employee_id, work_date, shift_start, shift_end):
        schedule = ScheduleService.get_by_id(id)
        if schedule:
            schedule.employee_id = employee_id
            schedule.work_date = work_date
            schedule.shift_start = shift_start
            schedule.shift_end = shift_end
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete(id):
        schedule = ScheduleService.get_by_id(id)
        if schedule:
            db.session.delete(schedule)
            db.session.commit()
            return True
        return False
