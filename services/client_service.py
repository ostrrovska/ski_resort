from models.client import Client, db

class ClientService:

    @staticmethod
    def get_all():
        return Client.query.all()

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