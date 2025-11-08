from models.pass_lift_usage import PassLiftUsage
from models import db
from services.pass_service import PassService
from services.lift_usage_service import LiftUsageService
from utils.query_helper import QueryHelper


class PassLiftUsageService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            PassLiftUsage,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals
        )

    @staticmethod
    def get_by_id(pass_id, lift_usage_id):
        return db.session.get(PassLiftUsage, (pass_id, lift_usage_id))

    @staticmethod
    def add(pass_id, lift_usage_id):
        if not PassService.get_by_id(pass_id):
            raise ValueError(f"Pass with id={pass_id} is not found.")
        if not LiftUsageService.get_by_id(lift_usage_id):
            raise ValueError(f"LiftUsage with id={lift_usage_id} is not found.")

        new_entry = PassLiftUsage(pass_id=pass_id, lift_usage_id=lift_usage_id)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @staticmethod
    def update(old_pass_id, old_lift_usage_id, new_pass_id, new_lift_usage_id):

        if not PassService.get_by_id(new_pass_id):
            raise ValueError(f"Pass with id={new_pass_id} is not found.")
        if not LiftUsageService.get_by_id(new_lift_usage_id):
            raise ValueError(f"LiftUsage with id={new_lift_usage_id} is not found.")

        entry = PassLiftUsageService.get_by_id(old_pass_id, old_lift_usage_id)
        if not entry:
            return None

        db.session.delete(entry)
        db.session.commit()

        updated_entry = PassLiftUsage(pass_id=new_pass_id, lift_usage_id=new_lift_usage_id)
        db.session.add(updated_entry)
        db.session.commit()

        return updated_entry

    @staticmethod
    def delete(pass_id, lift_usage_id):
        entry = PassLiftUsageService.get_by_id(pass_id, lift_usage_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False
