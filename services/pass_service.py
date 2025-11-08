import datetime

from models.passes import Pass, db
from services.client_service import ClientService
from services.pass_type_service import PassTypeService
from utils.query_helper import QueryHelper


class PassService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            Pass,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals,
        )

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

        pass_type = PassTypeService.get_by_id(pass_type_id)
        if not pass_type:
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