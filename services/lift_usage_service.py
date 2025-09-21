import datetime

from models.lift_usage import LiftUsage, db
from services.employee_service import EmployeeService
from services.lift_service import LiftService

class LiftUsageService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = LiftUsage.query
        sort_filter_options = {
            'id': LiftUsage.id,
            'client_id': LiftUsage.client_id,
            'lift_id': LiftUsage.lift_id,
            'usage_date': LiftUsage.usage_date,
            'usage_time_start': LiftUsage.usage_time_start,
            'usage_time_end': LiftUsage.usage_time_end,
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
        return LiftUsage.query.get(id)

    @staticmethod
    def add(client_id, lift_id, usage_date, usage_time_start, usage_time_end):
        client = EmployeeService.get_by_id(client_id)
        lift = LiftService.get_by_id(lift_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} is not found.")
        elif not lift:
            raise ValueError(f"Lift with ID {lift_id} is not found.")
        new_usage = LiftUsage(client_id, lift_id, usage_date, usage_time_start, usage_time_end)
        db.session.add(new_usage)
        db.session.commit()
        return new_usage

    @staticmethod
    def update(id, client_id, lift_id, usage_date, usage_time_start, usage_time_end):
        usage = LiftUsageService.get_by_id(id)
        if not usage:
            return None

        client = EmployeeService.get_by_id(client_id)
        lift = LiftService.get_by_id(lift_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} is not found.")
        elif not lift:
            raise ValueError(f"Lift with ID {lift_id} is not found.")

        usage.client_id = client_id
        usage.lift_id = lift_id
        usage.usage_date = usage_date
        usage.usage_time_start = usage_time_start
        usage.usage_time_end = usage_time_end
        db.session.commit()
        return usage

    @staticmethod
    def delete(id):
        usage = LiftUsageService.get_by_id(id)
        if usage:
            db.session.delete(usage)
            db.session.commit()
            return True
        return False