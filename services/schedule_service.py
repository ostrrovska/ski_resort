import datetime

from models.schedule import Schedule, db
from services.employee_service import EmployeeService
from utils.query_helper import QueryHelper


class ScheduleService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            Schedule,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals
        )

    @staticmethod
    def get_by_id(id):
        return Schedule.query.get(id)

    @staticmethod
    def add(employee_id, work_date, shift_start, shift_end):
        id = EmployeeService.get_by_id(employee_id)
        if not id:
            raise ValueError(f"Employee with ID {employee_id} is not found.")
        new_schedule = Schedule(employee_id, work_date, shift_start, shift_end)
        db.session.add(new_schedule)
        db.session.commit()
        return new_schedule

    @staticmethod
    def update(id, employee_id, work_date, shift_start, shift_end):
        schedule = ScheduleService.get_by_id(id)
        if not schedule:
            return None

        id = EmployeeService.get_by_id(employee_id)
        if not id:
            raise ValueError(f"Employee with ID {employee_id} is not found.")

        schedule.employee_id = employee_id
        schedule.work_date = work_date
        schedule.shift_start = shift_start
        schedule.shift_end = shift_end
        db.session.commit()
        return schedule

    @staticmethod
    def delete(id):
        schedule = ScheduleService.get_by_id(id)
        if schedule:
            db.session.delete(schedule)
            db.session.commit()
            return True
        return False
