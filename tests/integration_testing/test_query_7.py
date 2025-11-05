import pytest
from datetime import date
from models import db
from models.key import Key, AccessRight
from models.client import Client
from models.pass_type import PassType
from models.passes import Pass

# Імпортуємо сервіси, необхідні для налаштування
from services.client_service import ClientService
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
def pass_type_service():
    return PassTypeService()


@pytest.fixture(scope='function')
def pass_service():
    return PassService()


# --- Фікстура для наповнення БД даними ЛИШЕ для Запиту 7 ---

@pytest.fixture(scope='function')
def populate_db_for_query7(init_database, client_service, pass_type_service, pass_service):
    """Наповнює БД даними, необхідними для тестування Запиту 7."""

    # 1. Створюємо клієнтів
    c_alice = client_service.register("Alice Q7", "A_Q7", "1990-01-01", "111", "a_q7@t.com", "alice_q7", "pass")
    c_bob = client_service.register("Bob Q7", "B_Q7", "1991-02-02", "222", "b_q7@t.com", "bob_q7", "pass")
    c_charlie = client_service.register("Charlie Q7 (Unapproved)", "C_Q7", "1992-03-03", "333", "c_q7@t.com",
                                        "charlie_q7", "pass")
    c_dave = client_service.register("Dave Q7", "D_Q7", "1993-04-04", "444", "d_q7@t.com", "dave_q7", "pass")

    # 2. Схвалюємо деяких
    client_service.approve_registration(c_alice.key.id)
    client_service.approve_registration(c_bob.key.id)
    client_service.approve_registration(c_dave.key.id)
    # Charlie залишається несхваленим

    # 3. Створюємо типи абонементів
    pt_season = pass_type_service.add(name="Unlimited", limit_lifts=999, limit_hours=0, price=5000)
    pt_day = pass_type_service.add(name="Day Pass", limit_lifts=100, limit_hours=0, price=500)

    # 4. Створюємо абонементи (Passes)

    # Alice: Season Pass у Лютому 2025 (Має бути знайдена)
    pass_service.add(c_alice.id, pt_season.id, date(2025, 2, 10), date(2025, 2, 10), date(2025, 5, 10))

    # Bob: Day Pass у Лютому 2025 (Не той тип)
    pass_service.add(c_bob.id, pt_day.id, date(2025, 2, 12), date(2025, 2, 12), date(2025, 2, 13))

    # Alice: Season Pass у Березня 2025 (Не той місяць)
    pass_service.add(c_alice.id, pt_season.id, date(2025, 3, 10), date(2025, 3, 10), date(2025, 6, 10))

    # Charlie: Season Pass у Лютому 2025 (Несхвалений)
    pass_service.add(c_charlie.id, pt_season.id, date(2025, 2, 15), date(2025, 2, 15), date(2025, 5, 15))

    # Bob: Season Pass у Лютому 2024 (Не той рік)
    pass_service.add(c_bob.id, pt_season.id, date(2024, 2, 20), date(2024, 2, 20), date(2024, 5, 20))

    # Dave: Season Pass у Лютому 2025 (Має бути знайдений)
    pass_service.add(c_dave.id, pt_season.id, date(2025, 2, 5), date(2025, 2, 5), date(2025, 5, 5))

    return {
        "c_alice_id": c_alice.id,
        "c_bob_id": c_bob.id,
        "c_charlie_id": c_charlie.id,
        "c_dave_id": c_dave.id,
        "pass_name": "Unlimited"
    }


@pytest.mark.usefixtures("populate_db_for_query7")
class TestReport7FebruaryBuyers:
    """Групує тести для Запиту 7 (Клієнти з Season Pass у Лютому)."""

    def test_get_clients_success(self, report_service, populate_db_for_query7):
        """1. Тестує успішний пошук за 2025 рік, Лютий."""
        # Arrange
        pass_name = populate_db_for_query7["pass_name"]
        year = 2025
        month = 2

        alice_id = populate_db_for_query7["c_alice_id"]
        dave_id = populate_db_for_query7["c_dave_id"]

        # Act
        results = report_service.get_clients_bought_pass_by_month(pass_name, year, month)

        # Assert
        assert len(results) == 2
        client_ids = [r.client_id for r in results]

        assert alice_id in client_ids
        assert dave_id in client_ids

        # Bob (інший pass) і Charlie (unapproved) не повинні бути тут
        assert populate_db_for_query7["c_bob_id"] not in client_ids
        assert populate_db_for_query7["c_charlie_id"] not in client_ids

    def test_get_clients_wrong_year(self, report_service, populate_db_for_query7):
        """2. Тестує пошук за 2024 рік, Лютий."""
        # Arrange
        pass_name = populate_db_for_query7["pass_name"]
        year = 2024
        month = 2
        bob_id = populate_db_for_query7["c_bob_id"]

        # Act
        results = report_service.get_clients_bought_pass_by_month(pass_name, year, month)

        # Assert
        assert len(results) == 1
        assert results[0].client_id == bob_id

    def test_get_clients_wrong_month(self, report_service, populate_db_for_query7):
        """3. Тестує пошук за 2025 рік, Березень."""
        # Arrange
        pass_name = populate_db_for_query7["pass_name"]
        year = 2025
        month = 3
        alice_id = populate_db_for_query7["c_alice_id"]

        # Act
        results = report_service.get_clients_bought_pass_by_month(pass_name, year, month)

        # Assert
        assert len(results) == 1
        assert results[0].client_id == alice_id

    def test_get_clients_no_data(self, report_service, populate_db_for_query7):
        """4. Тестує пошук за 2023 рік (немає даних)."""
        # Arrange
        pass_name = populate_db_for_query7["pass_name"]
        year = 2023
        month = 2

        # Act
        results = report_service.get_clients_bought_pass_by_month(pass_name, year, month)

        # Assert
        assert len(results) == 0

    def test_get_clients_wrong_pass_name(self, report_service, populate_db_for_query7):
        """5. Тестує пошук з неправильною назвою абонемента."""
        # Arrange
        pass_name = "Nonexistent Pass"
        year = 2025
        month = 2

        # Act
        results = report_service.get_clients_bought_pass_by_month(pass_name, year, month)

        # Assert
        assert len(results) == 0

    def test_get_clients_handles_null_params(self, report_service):
        """6. Тестує, що сервіс повертає [] при None параметрах."""
        # Act
        results1 = report_service.get_clients_bought_pass_by_month(None, 2025, 2)
        results2 = report_service.get_clients_bought_pass_by_month("Unlimited", None, 2)
        results3 = report_service.get_clients_bought_pass_by_month("Unlimited", 2025, None)

        # Assert
        assert results1 == []
        assert results2 == []
        assert results3 == []