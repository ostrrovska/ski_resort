import datetime

from models.lift_usage import LiftUsage, db
from services.employee_service import EmployeeService
from services.client_service import ClientService
from services.lift_service import LiftService
from utils.query_helper import QueryHelper


class LiftUsageService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            LiftUsage,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals,
        )

    @staticmethod
    def get_by_id(id):
        return LiftUsage.query.get(id)

    @staticmethod
    def add(client_id, lift_id, usage_date, usage_time_start, usage_time_end):
        client = ClientService.get_by_id(client_id)
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

        client = ClientService.get_by_id(client_id)
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