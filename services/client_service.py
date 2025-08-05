from models.client import Client, db

class ClientService:

    @staticmethod
    def register(full_name, document_id, date_of_birth, phone_number, email, username, password):
        existing_client = Client.query.filter_by(username=username).first()
        if existing_client:
            return None
        new_client = Client(full_name=full_name, document_id=document_id, date_of_birth=date_of_birth,
                            phone_number=phone_number, email=email, username=username
                            )
        new_client.set_password(password)
        db.session.add(new_client)
        db.session.commit()
        return new_client

    @staticmethod
    def login(username, password):
        user = Client.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def get_all(sort_by = None, sort_order = 'asc'):
        query = Client.query
        sort_options = {
            'id': Client.id,
            'full_name': Client.full_name,
            'document_id': Client.document_id,
            'date_of_birth': Client.date_of_birth,
            'phone_number': Client.phone_number,
            'email': Client.email
        }
        if sort_by in sort_options:
            if sort_order == 'desc':
                query = query.order_by(sort_options[sort_by].desc())
            else:
                query = query.order_by(sort_options[sort_by])
        return query.all()

    @staticmethod
    def get_by_id(id):
        return Client.query.get(id)

    @staticmethod
    def add(full_name, document_id, date_of_birth, phone_number, email):
        new_client = Client(full_name, document_id, date_of_birth, phone_number, email)
        db.session.add(new_client)
        db.session.commit()
        return new_client

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
            db.session.delete(client)
            db.session.commit()
            return True
        return False