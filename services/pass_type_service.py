from models.pass_type import PassType, db

class PassTypeService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = PassType.query
        sort_filter_options = {
            'id': PassType.id,
            'name': PassType.name,
            'limit_lifts': PassType.limit_lifts,
            'limit_hours': PassType.limit_hours,
            'price': PassType.price
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
        pass_type = PassTypeService.get_by_id(id)
        if pass_type:
            db.session.delete(pass_type)
            db.session.commit()
            return True
        return False