import os
from datetime import date, time, timedelta
from app import app
from models import db
from models.employee import Employee
from models.schedule import Schedule
from models.client import Client
from models.key import Key, AccessRight
from models.equipment_type import EquipmentType
from models.equipment import Equipment
from models.tariff import Tariff
from models.lift import Lift
from models.lift_usage import LiftUsage
from models.pass_type import PassType
from models.passes import Pass
from models.rental import Rental
from models.rental_equipment import RentalEquipment
from models.pass_lift_usage import PassLiftUsage


def seed_data():
    print("Starting database seed...")

    # Використовуємо 'app_context'
    with app.app_context():
        # Видаляємо всі існуючі дані та таблиці
        print("Dropping all tables...")
        db.drop_all()
        # Створюємо всі таблиці згідно з моделями
        print("Creating all tables...")
        db.create_all()

        # --- 1. Створення Працівників (Employees) ---
        print("Creating employees...")
        emp1 = Employee(
            full_name="John Doe",
            position="Rental Manager",
            salary=35000,
            phone_number="0501112233",
            email="john.doe@resort.ua"
        )
        emp2 = Employee(
            full_name="Jane Smith",
            position="Administrator",
            salary=38000,
            phone_number="0504445566",
            email="jane.smith@resort.ua"
        )
        db.session.add_all([emp1, emp2])
        db.session.commit()
        print(f"Created employees with IDs: {emp1.id}, {emp2.id}")

        # --- 2. Створення Клієнтів (Clients) та Ключів (Keys) ---
        print("Creating pending clients...")

        # Client 1
        key1 = Key(login="client_john", access_right=AccessRight.AUTHORIZED, is_approved=False)
        key1.set_password("pass123")
        db.session.add(key1)
        db.session.commit()
        client1 = Client(
            full_name="John Apple",
            document_id="AA123456",
            date_of_birth=date(1990, 3, 9),
            phone_number="0671112233",
            email="john.apple@gmail.com",
            authorization_fkey=key1.id
        )

        # Client 2
        key2 = Key(login="client_jane", access_right=AccessRight.AUTHORIZED, is_approved=False)
        key2.set_password("pass456")
        db.session.add(key2)
        db.session.commit()
        client2 = Client(
            full_name="Jane Oak",
            document_id="BB654321",
            date_of_birth=date(1985, 12, 3),
            phone_number="0994445566",
            email="jane.oak@gmail.com",
            authorization_fkey=key2.id
        )

        #Admin
        key_admin = Key(login="a", access_right=AccessRight.ADMIN, is_approved=True)
        key_admin.set_password("a")
        db.session.add(key_admin)
        db.session.commit()
        client_admin = Client(
            full_name="Kateryna",
            document_id="1234",
            date_of_birth=date(2005, 12, 13),
            phone_number="0981739760",
            email="ostrovskakatia@gmail.com",
            authorization_fkey=key_admin.id
        )

        db.session.add_all([client1, client2, client_admin])
        db.session.commit()
        print(f"Created clients with IDs: {client1.id}, {client2.id}. All are pending approval.")

        # --- 3. Базові сутності (Lifts, Equipment Types, Pass Types) ---
        print("Creating base entities (lifts, equipment types, pass types)...")

        # Lifts
        lift1 = Lift(name="Lift A (Beginner)", height=300)
        lift2 = Lift(name="Lift B (Intermediate)", height=700)
        lift3 = Lift(name="Lift C (Advanced)", height=1200)

        # Equipment Types
        et1 = EquipmentType(name="Standard Skis", description="Skis for beginners and intermediate level.")
        et2 = EquipmentType(name="Snowboard", description="Snowboards for all styles.")
        et3 = EquipmentType(name="Helmet", description="Protective helmets.")

        # Pass Types
        pt1 = PassType(name="1-Day Pass", limit_lifts=100, limit_hours=8, price=1200)
        pt2 = PassType(name="10 Lifts Pass", limit_lifts=10, limit_hours=0, price=800)
        pt3 = PassType(name="3 Hours Pass", limit_lifts=0, limit_hours=3, price=600)

        db.session.add_all([lift1, lift2, lift3, et1, et2, et3, pt1, pt2, pt3])
        db.session.commit()
        print("Base entities committed.")

        # --- 4. Залежні базові сутності (Tariffs, Equipment) ---
        print("Creating dependent base entities (tariffs, equipment)...")

        # Tariffs (depend on EquipmentType)
        t1 = Tariff(equipment_type_id=et1.id, price_per_hour=150, price_per_day=500, weekday_discount=10)
        t2 = Tariff(equipment_type_id=et2.id, price_per_hour=180, price_per_day=600, weekday_discount=10)
        t3 = Tariff(equipment_type_id=et3.id, price_per_hour=50, price_per_day=150, weekday_discount=5)

        # Equipment (depend on EquipmentType)
        eq1 = Equipment(type_id=et1.id, model="Rossignol Hero", is_available=True)
        eq2 = Equipment(type_id=et1.id, model="Atomic Redster", is_available=True)
        eq3 = Equipment(type_id=et2.id, model="Burton Custom", is_available=True)
        eq4 = Equipment(type_id=et3.id, model="Giro Ledge", is_available=True)

        db.session.add_all([t1, t2, t3, eq1, eq2, eq3, eq4])
        db.session.commit()
        print("Dependent base entities committed.")

        # --- 5. Створення пов'язаних даних (Schedules, Passes, Rentals, Usages) ---
        print("Creating linked data (schedules, passes, rentals, usages)...")
        today = date.today()

        # Schedules (depend on Employee)
        sch1 = Schedule(employee_id=emp1.id, work_date=today, shift_start=time(8, 0), shift_end=time(17, 0))
        sch2 = Schedule(employee_id=emp2.id, work_date=today, shift_start=time(9, 0), shift_end=time(18, 0))

        # Passes (depend on Client, PassType)
        pass1 = Pass(
            client_id=client1.id, pass_type_id=pt1.id,
            purchase_date=today - timedelta(days=1), valid_from=today - timedelta(days=1), valid_to=today,
            remaining_lifts=pt1.limit_lifts, remaining_hours=pt1.limit_hours
        )
        pass2 = Pass(
            client_id=client2.id, pass_type_id=pt2.id,
            purchase_date=today, valid_from=today, valid_to=today + timedelta(days=30),
            remaining_lifts=pt2.limit_lifts, remaining_hours=pt2.limit_hours
        )

        # Rentals (depend on Client, Employee)
        rent1 = Rental(
            client_id=client1.id, employee_id=emp1.id,
            rental_date=today, start_time=time(9, 15), end_time=time(17, 15),
            rental_type="daily", total_price=t1.price_per_day
        )

        # Lift Usages (depend on Client, Lift)
        lu1 = LiftUsage(
            client_id=client1.id, lift_id=lift1.id,
            usage_date=today, usage_time_start=time(9, 30), usage_time_end=time(9, 35)
        )
        lu2 = LiftUsage(
            client_id=client2.id, lift_id=lift2.id,
            usage_date=today, usage_time_start=time(9, 45), usage_time_end=time(9, 52)
        )

        db.session.add_all([sch1, sch2, pass1, pass2, rent1, lu1, lu2])
        db.session.commit()
        print("Linked data committed.")

        # --- 6. Створення даних для таблиць зв'язку (Junction Tables) ---
        print("Creating junction table data (rental equipment, pass usages)...")

        # RentalEquipment (depend on Rental, Equipment)
        re1 = RentalEquipment(rental_id=rent1.id, equipment_id=eq1.id)
        re2 = RentalEquipment(rental_id=rent1.id, equipment_id=eq4.id)  # (Skis + Helmet)

        # PassLiftUsage (depend on Pass, LiftUsage)
        plu1 = PassLiftUsage(pass_id=pass1.id, lift_usage_id=lu1.id)
        plu2 = PassLiftUsage(pass_id=pass2.id, lift_usage_id=lu2.id)

        db.session.add_all([re1, re2, plu1, plu2])

        # --- Фінальний Commit ---
        db.session.commit()
        print("Database seed completed successfully!")


if __name__ == "__main__":
    # Переконайтеся, що .env файл завантажено, якщо скрипт запускається окремо
    from dotenv import load_dotenv

    load_dotenv()

    # Перевірка, чи завантажено URI бази даних
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        print("Error: SQLALCHEMY_DATABASE_URI is not set.")
        print("Please ensure your .env file is in the root directory and contains the database URL.")
    else:
        seed_data()