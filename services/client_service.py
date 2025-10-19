import datetime

from models.client import Client, db
from models.key import Key, AccessRight


class ClientService:

    @staticmethod
    def register(full_name, document_id, date_of_birth, phone_number, email, login, password):
        if Key.query.filter_by(login=login).first():
            return None
        new_key = Key(login=login, access_right=AccessRight.AUTHORIZED, is_approved=False)
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
            if not key.is_approved:
                return 'pending'
            return key
        return 'invalid'

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        # --- Змінюємо запит, щоб об'єднати Client та Key ---
        query = db.session.query(Client, Key).join(Key, Client.authorization_fkey == Key.id).filter(Key.is_approved == True)

        # --- Оновлюємо словник для сортування/фільтрації ---
        sort_filter_options = {
            'id': Client.id,
            'full_name': Client.full_name,
            'document_id': Client.document_id,
            'date_of_birth': Client.date_of_birth,
            'phone_number': Client.phone_number,
            'email': Client.email,
            'login': Key.login,  # Можна додати сортування/фільтрацію за логіном
            'access_right': Key.access_right  # Можна додати сортування/фільтрацію за роллю
        }

        # --- Логіка фільтрації ---
        if filter_by in sort_filter_options and filter_value is not None:
            column_attr = sort_filter_options[filter_by]
            model = Client if hasattr(Client, filter_by) else Key  # Визначаємо модель для колонки
            column = getattr(model, filter_by)  # Отримуємо атрибут колонки SQLAlchemy

            # Обробка різних типів даних
            if isinstance(column.type, db.Integer):
                try:
                    query = query.filter(column == int(filter_value))
                except ValueError:
                    pass  # Ігноруємо нечислові значення для числових колонок
            elif isinstance(column.type, db.Date):
                try:
                    date_value = datetime.datetime.strptime(filter_value, "%Y-%m-%d").date()
                    query = query.filter(column == date_value)
                except ValueError:
                    pass  # Ігноруємо некоректний формат дати
            elif isinstance(column.type, db.Enum):
                # Дозволяємо фільтрацію за роллю (якщо filter_by == 'access_right')
                try:
                    # Перетворюємо рядок filter_value на член Enum
                    enum_value = AccessRight(filter_value.lower())
                    query = query.filter(column == enum_value)
                except ValueError:
                    pass  # Ігноруємо, якщо значення не є валідною роллю
            else:  # Для рядкових типів (String)
                query = query.filter(column.ilike(f'%{filter_value}%'))

        # --- Логіка сортування ---
        if sort_by in sort_filter_options:
            column_attr = sort_filter_options[sort_by]
            model = Client if hasattr(Client, sort_by) else Key
            column = getattr(model, sort_by)

            if sort_order == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

        # Повертаємо список кортежів (Client, Key)
        return query.all()

    @staticmethod
    def set_access_right(client_id, new_role: AccessRight):
        """Змінює роль доступу для клієнта."""
        client = ClientService.get_by_id(client_id)
        if not client:
            return False  # Клієнта не знайдено

        key = Key.query.get(client.authorization_fkey)
        if key:
            key.access_right = new_role
            db.session.commit()
            return True
        return False  # Ключ не знайдено (малоймовірно)

    @staticmethod
    def get_pending_registrations():
        """Повертає всіх користувачів, які очікують на підтвердження."""
        return db.session.query(Client, Key).join(Key, Client.authorization_fkey == Key.id).filter(
            Key.is_approved == False).all()

    @staticmethod
    def approve_registration(key_id):
        """Підтверджує реєстрацію за ID ключа."""
        key = Key.query.get(key_id)
        if key and not key.is_approved:
            key.is_approved = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def reject_registration(key_id):
        """Відхиляє та видаляє заявку на реєстрацію (клієнта і ключ)."""
        key = Key.query.get(key_id)
        if key:
            # Знаходимо пов'язаного клієнта
            client = Client.query.filter_by(authorization_fkey=key.id).first()
            if client:
                db.session.delete(client)

            db.session.delete(key)
            db.session.commit()
            return True
        return False

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