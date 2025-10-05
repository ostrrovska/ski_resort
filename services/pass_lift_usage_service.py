from models.pass_lift_usage import PassLiftUsage
from models import db
from services.pass_service import PassService
from services.lift_usage_service import LiftUsageService


class PassLiftUsageService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = PassLiftUsage.query

        if filter_by and filter_value is not None:
            if filter_by in ['pass_id', 'lift_usage_id']:
                query = query.filter(getattr(PassLiftUsage, filter_by) == filter_value)

        if sort_by in ['pass_id', 'lift_usage_id']:
            sort_column = getattr(PassLiftUsage, sort_by)
            if sort_order == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

        return query.all()

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
