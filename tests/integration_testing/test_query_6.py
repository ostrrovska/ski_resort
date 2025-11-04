import pytest
from datetime import date, time
from models import db
from models.key import Key, AccessRight
from models.client import Client
from models.lift import Lift
from models.lift_usage import LiftUsage
from models.pass_type import PassType
from models.passes import Pass

# Імпортуємо сервіси, необхідні для налаштування
from services.client_service import ClientService
from services.lift_service import LiftService
from services.lift_usage_service import LiftUsageService
from services.pass_type_service import PassTypeService
from services.pass_service import PassService
from services.report_service import ReportService

# Автоматично застосовуємо 'app_context' з conftest.py до всіх тестів у цьому файлі
pytestmark = pytest.mark.usefixtures("app_context")


# --- Базові фікстури ---

@pytest.fixture(scope='function')
def init_database(app_context):
    """Створює всі таблиці в пам'яті перед тестом і видаляє їх після."""
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def report_service():
    """Надає екземпляр сервісу, що тестується."""
    return ReportService()


@pytest.fixture(scope='function')
def client_service():
    return ClientService()


@pytest.fixture(scope='function')
def lift_service():
    return LiftService()


@pytest.fixture(scope='function')
def lift_usage_service():
    return LiftUsageService()


@pytest.fixture(scope='function')
def pass_type_service():
    return PassTypeService()


@pytest.fixture(scope='function')
def pass_service():
    return PassService()


# --- Фікстура для наповнення БД даними ЛИШЕ для Запиту 6 ---

@pytest.fixture(scope='function')
def populate_db_for_query6(init_database, client_service, lift_service, lift_usage_service, pass_type_service,
                           pass_service):
    """Наповнює БД даними, необхідними для тестування Запиту 6."""

    # 1. Створюємо клієнтів
    c_alice = client_service.register("Alice Q6", "A_Q6", "1990-01-01", "111", "a_q6@t.com", "alice_q6", "pass")
    c_bob = client_service.register("Bob Q6", "B_Q6", "1991-02-02", "222", "b_q6@t.com", "bob_q6", "pass")
    c_charlie = client_service.register("Charlie Q6 (Unapproved)", "C_Q6", "1992-03-03", "333", "c_q6@t.com",
                                        "charlie_q6",
                                        "pass")
    c_dave = client_service.register("Dave Q6", "D_Q6", "1993-04-04", "444", "d_q6@t.com", "dave_q6", "pass")

    # 2. Схвалюємо деяких
    client_service.approve_registration(c_alice.key.id)
    client_service.approve_registration(c_bob.key.id)
    client_service.approve_registration(c_dave.key.id)
    # Charlie залишається несхваленим

    # 3. Створюємо типи абонементів
    pt_10_lift = pass_type_service.add(name="10 Lifts", limit_lifts=10, limit_hours=0, price=500)
    pt_100_lift = pass_type_service.add(name="100 Lifts", limit_lifts=100, limit_hours=0, price=5000)

    # 4. Створюємо абонементи (Passes)
    today = date.today()
    pass_alice = pass_service.add(c_alice.id, pt_10_lift.id, today, today, today)
    pass_bob = pass_service.add(c_bob.id, pt_100_lift.id, today, today, today)
    pass_charlie = pass_service.add(c_charlie.id, pt_10_lift.id, today, today, today)
    pass_dave = pass_service.add(c_dave.id, pt_10_lift.id, today, today, today)

    # Модифікуємо remaining_lifts
    pass_alice.remaining_lifts = 0  # Alice вичерпала
    pass_bob.remaining_lifts = 50  # Bob не вичерпав
    pass_charlie.remaining_lifts = 0  # Charlie (несхвалений) вичерпав
    pass_dave.remaining_lifts = -2  # Dave вичерпав (<= 0)
    db.session.commit()

    # 5. Створюємо підйомник
    lift_a = lift_service.add(name="Main Lift", height=500)

    # 6. Створюємо тестові дати
    test_day = date(2025, 12, 10)
    other_day = date(2025, 12, 11)
    t1 = time(9, 0)
    t2 = time(10, 0)

    # 7. Створюємо LiftUsage
    # Alice (схвалена) - 10 підйомів
    for _ in range(10):
        lift_usage_service.add(c_alice.id, lift_a.id, test_day, t1, t2)

    # Bob (схвалений) - 16 підйомів
    for _ in range(16):
        lift_usage_service.add(c_bob.id, lift_a.id, test_day, t1, t2)

    # Charlie (несхвалений) - 20 підйомів
    for _ in range(20):
        lift_usage_service.add(c_charlie.id, lift_a.id, test_day, t1, t2)

    # Dave (схвалений) - 15 підйомів (не > 15)
    for _ in range(15):
        lift_usage_service.add(c_dave.id, lift_a.id, test_day, t1, t2)

    # Bob (схвалений) - 5 підйомів (інший день)
    for _ in range(5):
        lift_usage_service.add(c_bob.id, lift_a.id, other_day, t1, t2)

    return {
        "c_alice_id": c_alice.id,
        "c_bob_id": c_bob.id,
        "c_charlie_id": c_charlie.id,
        "c_dave_id": c_dave.id,
        "test_day": test_day,
        "other_day": other_day
    }


@pytest.mark.usefixtures("populate_db_for_query6")
class TestReport6ClientPassStats:
    """Групує тести для Запиту 6 (Статистика абонементів клієнтів)."""

    def test_get_clients_with_exhausted_passes(self, report_service, populate_db_for_query6):
        """1. Тестує отримання клієнтів, які вичерпали абонементи."""
        # Arrange
        alice_id = populate_db_for_query6["c_alice_id"]
        dave_id = populate_db_for_query6["c_dave_id"]

        # Act
        results = report_service.get_clients_with_exhausted_passes()

        # Assert
        assert len(results) == 2  # Alice і Dave

        client_ids = [r.client_id for r in results]
        assert alice_id in client_ids
        assert dave_id in client_ids

        # Bob (50 lifts) і Charlie (unapproved) не повинні бути тут
        assert populate_db_for_query6["c_bob_id"] not in client_ids
        assert populate_db_for_query6["c_charlie_id"] not in client_ids

    def test_get_clients_with_over_15_lifts_daily_success(self, report_service, populate_db_for_query6):
        """2. Тестує отримання клієнтів, що зробили > 15 підйомів за test_day."""
        # Arrange
        test_day = populate_db_for_query6["test_day"]
        bob_id = populate_db_for_query6["c_bob_id"]

        # Act
        results = report_service.get_clients_with_over_15_lifts_daily(test_day)

        # Assert
        assert len(results) == 1  # Тільки Bob
        assert results[0].client_id == bob_id
        assert results[0].lift_count == 16

        # Alice (10), Dave (15) і Charlie (unapproved) не повинні бути тут
        client_ids = [r.client_id for r in results]
        assert populate_db_for_query6["c_alice_id"] not in client_ids
        assert populate_db_for_query6["c_dave_id"] not in client_ids
        assert populate_db_for_query6["c_charlie_id"] not in client_ids

    def test_get_clients_with_over_15_lifts_daily_no_one(self, report_service, populate_db_for_query6):
        """3. Тестує день (other_day), коли ніхто не зробив > 15 підйомів."""
        # Arrange
        other_day = populate_db_for_query6["other_day"]

        # Act
        results = report_service.get_clients_with_over_15_lifts_daily(other_day)

        # Assert
        assert len(results) == 0  # Bob зробив лише 5 підйомів

    def test_get_clients_with_over_15_lifts_daily_handles_none(self, report_service):
        """4. Тестує, що функція > 15 підйомів повертає [] при даті None."""
        # Act
        results = report_service.get_clients_with_over_15_lifts_daily(None)
        # Assert
        assert results == []

    def test_exhausted_passes_ignores_unapproved(self, report_service, populate_db_for_query6):
        """5. (Дублює логіку test_get_clients_with_exhausted_passes) Переконується, що несхвалені не включені."""
        # Arrange
        unapproved_charlie_id = populate_db_for_query6["c_charlie_id"]

        # Act
        results = report_service.get_clients_with_exhausted_passes()
        client_ids = [r.client_id for r in results]

        # Assert
        assert unapproved_charlie_id not in client_ids
        assert len(results) == 2

    def test_over_15_lifts_ignores_unapproved(self, report_service, populate_db_for_query6):
        """6. (Дублює логіку test_get_clients_with_over_15_lifts_daily_success) Переконується, що несхвалені не включені."""
        # Arrange
        test_day = populate_db_for_query6["test_day"]
        unapproved_charlie_id = populate_db_for_query6["c_charlie_id"]

        # Act
        results = report_service.get_clients_with_over_15_lifts_daily(test_day)
        client_ids = [r.client_id for r in results]

        # Assert
        # Charlie (20 lifts) не повинен бути у списку, оскільки він несхвалений
        assert unapproved_charlie_id not in client_ids
        assert len(results) == 1  # Тільки Bob (16 lifts)