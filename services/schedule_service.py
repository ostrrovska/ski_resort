import datetime

from models.schedule import Schedule, db


class ScheduleService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = Schedule.query
        sort_filter_options = {
            'id': Schedule.id,
            'employee_id': Schedule.employee_id,
            'work_date': Schedule.work_date,
            'shift_start': Schedule.shift_start,
            'shift_end': Schedule.shift_end
        }
        if sort_by in sort_filter_options:
            if sort_order == 'desc':
                query = query.order_by(sort_filter_options[sort_by].desc())
            else:
                query = query.order_by(sort_filter_options[sort_by])

        if filter_by in sort_filter_options and filter_value:
            column = sort_filter_options[filter_by]
            if isinstance(column.type, db.Integer):
                query = query.filter(column == int(filter_value))
            elif isinstance(column.type, db.Date):
                # Parse filter_value to a date object
                date_value = datetime.datetime.strptime(filter_value, "%Y-%m-%d").date()
                query = query.filter(column == date_value)
            elif isinstance(column.type, db.Time):
                # Parse filter_value to a time object
                time_value = datetime.datetime.strptime(filter_value, "%H:%M:%S").time()
                query = query.filter(column == time_value)
            else:
                query = query.filter(column.ilike(f'%{filter_value}%'))
        return query.all()

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
