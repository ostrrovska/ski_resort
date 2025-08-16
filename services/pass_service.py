import datetime

from models.passes import Pass, db
from services.client_service import ClientService
from services.pass_type_service import PassTypeService

class PassService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = Pass.query
        sort_filter_options = {
            'id': Pass.id,
            'pass_type_id': Pass.pass_type_id,
            'client_id': Pass.client_id,
            'purchase_date': Pass.purchase_date,
            'valid_from': Pass.valid_from,
            'valid_to': Pass.valid_to,
            'remaining_lifts': Pass.remaining_lifts,
            'remaining_hours': Pass.remaining_hours
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
            else:
                query = query.filter(column.ilike(f'%{filter_value}%'))
        return query.all()

    @staticmethod
    def get_by_id(id):
        return Pass.query.get(id)

    @staticmethod
    def add(client_id, pass_type_id, purchase_date, valid_from, valid_to):
        client = ClientService.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} is not found.")

        pass_type = PassTypeService.get_by_id(pass_type_id)
        if not pass_type:
            raise ValueError(f"Pass type with ID {pass_type_id} is not found.")

        new_pass = Pass(client_id, pass_type_id, purchase_date, valid_from,
                        valid_to, pass_type.limit_lifts, pass_type.limit_hours)
        db.session.add(new_pass)
        db.session.commit()
        return new_pass

    @staticmethod
    def update(id, client_id, pass_type_id, purchase_date, valid_from, valid_to, remaining_lifts, remaining_hours):
        pass_ = PassService.get_by_id(id)
        if not pass_:
            return None

        client = ClientService.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} is not found.")

        pass_type_id = PassTypeService.get_by_id(pass_type_id)
        if not pass_type_id:
            raise ValueError(f"Pass type with ID {pass_type_id} is not found.")

        pass_.client_id = client_id
        pass_.pass_type_id = pass_type_id
        pass_.purchase_date = purchase_date
        pass_.valid_from = valid_from
        pass_.valid_to = valid_to
        pass_.remaining_lifts = remaining_lifts
        pass_.remaining_hours = remaining_hours
        db.session.commit()
        return pass_

    @staticmethod
    def delete(id):
        pass_ = PassService.get_by_id(id)
        if pass_:
            db.session.delete(pass_)
            db.session.commit()
            return True
        return False

