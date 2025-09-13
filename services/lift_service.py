from models.lift import Lift, db


class LiftService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = Lift.query
        sort_filter_options = {
            'id': Lift.id,
            'name': Lift.name,
            'height': Lift.height
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
            else:
                query = query.filter(column.ilike(f'%{filter_value}%'))
        return query.all()

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

