import datetime

from models.client import Client, db
from models.key import Key, AccessRight
from models.lift_usage import LiftUsage
from models.passes import Pass
from models.rental import Rental
from models.saved_view import SavedView
from utils.query_helper import QueryHelper
from sqlalchemy import String, Enum


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
    def get_all(sort_by=None, sort_order='asc',
                filter_cols=None, filter_ops=None, filter_vals=None):  # <-- Тільки нові параметри

        # 1. Початковий запит з JOIN
        query = db.session.query(Client, Key).join(Key, Client.authorization_fkey == Key.id).filter(
            Key.is_approved == True)

        # 2. Створюємо карту моделей
        models_map = {'Client': Client, 'Key': Key}

        # 3. Видалено логіку конвертації старих фільтрів

        # 4. Застосовуємо фільтри та сортування
        query = QueryHelper.apply_filters(query, models_map, filter_cols, filter_ops, filter_vals)
        query = QueryHelper.apply_sorting(query, models_map, sort_by, sort_order)

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
        from services.pass_service import PassService
        from services.rental_service import RentalService
        from services.lift_usage_service import LiftUsageService
        client = ClientService.get_by_id(id)
        if client:
            key = Key.query.get(client.authorization_fkey)

            # --- ПОЧАТОК ЗМІН ---
            # Каскадне видалення: викликаємо сервіси для всіх залежностей

            # 1. Saved Views (не має дітей)
            SavedView.query.filter_by(client_id=client.id).delete(synchronize_session=False)

            # 2. Passes (PassService видалить PassLiftUsage і PassRentalUsage)
            passes_to_delete = Pass.query.filter_by(client_id=client.id).all()
            for pass_ in passes_to_delete:
                PassService.delete(pass_.id)

            # 3. Rentals (RentalService видалить RentalEquipment і PassRentalUsage)
            rentals_to_delete = Rental.query.filter_by(client_id=client.id).all()
            for rental in rentals_to_delete:
                RentalService.delete(rental.id)

            # 4. Lift Usages (LiftUsageService видалить PassLiftUsage)
            usages_to_delete = LiftUsage.query.filter_by(client_id=client.id).all()
            for usage in usages_to_delete:
                LiftUsageService.delete(usage.id)
            # --- КІНЕЦЬ ЗМІН ---

            if key:
                db.session.delete(key)
            db.session.delete(client)
            db.session.commit()
            return True
        return False