import datetime

from models.client import Client, db
from models.key import Key, AccessRight


class ClientService:

    @staticmethod
    def register(full_name, document_id, date_of_birth, phone_number, email, login, password):
        if Key.query.filter_by(login=login).first():
            return None
        new_key = Key(login=login, access_right=AccessRight.AUTHORIZED)
        new_key.set_password(password)

        db.session.add(new_key)
        db.session.commit()

        new_client = Client(
            full_name=full_name,
            document_id=document_id,
            date_of_birth=date_of_birth,
            phone_number=phone_number,
            email=email,
            authorization_fkey=new_key.id
        )
        db.session.add(new_client)
        db.session.commit()

        return new_client

    @staticmethod
    def login(login, password):
        key = Key.query.filter_by(login=login).first()
        if key and key.check_password(password):
            return key
        return None

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = Client.query
        sort_filter_options = {
            'id': Client.id,
            'full_name': Client.full_name,
            'document_id': Client.document_id,
            'date_of_birth': Client.date_of_birth,
            'phone_number': Client.phone_number,
            'email': Client.email
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
        return Client.query.get(id)

    @staticmethod
    def update(id, full_name, document_id, date_of_birth, phone_number, email):
        client = ClientService.get_by_id(id)
        if client:
            client.full_name = full_name
            client.document_id = document_id
            client.date_of_birth = date_of_birth
            client.phone_number = phone_number
            client.email = email
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete(id):
        client = ClientService.get_by_id(id)
        if client:
            key = Key.query.get(client.authorization_fkey)
            if key:
                db.session.delete(key)
            db.session.delete(client)
            db.session.commit()
            return True
        return False