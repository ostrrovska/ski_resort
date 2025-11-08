from models.lift import Lift, db
from utils.query_helper import QueryHelper


class LiftService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None,
                filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            Lift,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals,
            filter_by=filter_by,
            filter_value=filter_value,
        )

    @staticmethod
    def get_by_id(id):
        return Lift.query.get(id)

    @staticmethod
    def add(name, height):
        new_lift = Lift(name, height)
        db.session.add(new_lift)
        db.session.commit()
        return new_lift

    @staticmethod
    def update(id, name, height):
        lift = LiftService.get_by_id(id)
        if not lift:
            return None

        lift.name = name
        lift.height = height
        db.session.commit()
        return lift

    @staticmethod
    def delete(id):
        lift = LiftService.get_by_id(id)
        if lift:
            db.session.delete(lift)
            db.session.commit()
            return True
        return False

