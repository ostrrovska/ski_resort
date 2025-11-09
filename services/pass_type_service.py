from models.pass_type import PassType, db
from models.passes import Pass
from utils.query_helper import QueryHelper


class PassTypeService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None,
                filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            PassType,
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
        return PassType.query.get(id)

    @staticmethod
    def add(name, limit_lifts, limit_hours, price):
        new_pass_type = PassType(name, limit_lifts, limit_hours, price)
        db.session.add(new_pass_type)
        db.session.commit()
        return new_pass_type

    @staticmethod
    def update(id, name, limit_lifts, limit_hours, price):
        pass_type = PassTypeService.get_by_id(id)
        if pass_type:
            pass_type.name = name
            pass_type.limit_lifts = limit_lifts
            pass_type.limit_hours = limit_hours
            pass_type.price = price
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete(id):
        from services.pass_service import PassService
        pass_type = PassTypeService.get_by_id(id)
        if pass_type:
            # --- ПОЧАТОК ЗМІН ---
            # Каскадне видалення
            passes_to_delete = Pass.query.filter_by(pass_type_id=id).all()
            for pass_ in passes_to_delete:
                PassService.delete(pass_.id)  # PassService вже обробляє своїх дітей
            # --- КІНЕЦЬ ЗМІН ---

            db.session.delete(pass_type)
            db.session.commit()
            return True
        return False