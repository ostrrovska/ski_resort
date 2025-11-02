import pytest
from datetime import date
from models import db
from models.key import Key, AccessRight
from models.client import Client
from models.pass_type import PassType
from models.passes import Pass

# Імпортуємо сервіси, необхідні для налаштування даних та тестування
from services.client_service import ClientService
from services.pass_type_service import PassTypeService
from services.pass_service import PassService
from services.report_service import ReportService

# Автоматично застосовуємо 'app_context' з conftest.py до всіх тестів у цьому файлі
pytestmark = pytest.mark.usefixtures("app_context")


# --- Базові фікстури для цього тестового файлу ---

@pytest.fixture(scope='function')
def init_database(app_context):
    """Створює всі таблиці в пам'яті перед тестом і видаляє їх після."""
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')  # <- ЗМІНЕНО: class -> function
def report_service():
    """Надає екземпляр сервісу, що тестується."""
    return ReportService()


@pytest.fixture(scope='function')  # <- ЗМІНЕНО: class -> function
def client_service():
    """Надає ClientService для створення тестових даних."""
    return ClientService()


@pytest.fixture(scope='function')  # <- ЗМІНЕНО: class -> function
def pass_type_service():
    """Надає PassTypeService для створення тестових даних."""
    return PassTypeService()


@pytest.fixture(scope='function')  # <- ЗМІНЕНО: class -> function
def pass_service():
    """Надає PassService для створення тестових даних."""
    return PassService()


# --- Фікстура для наповнення БД даними ЛИШЕ для Запиту 3 ---

@pytest.fixture(scope='function')  # <- ЗМІНЕНО: class -> function
def populate_db_for_query3(init_database, client_service, pass_type_service, pass_service):
    """
    Наповнює БД даними, необхідними виключно для тестування звітів
    про продажі абонементів (Запит 3).
    """
    # 1. Створюємо клієнтів
    client_alice = client_service.register("Alice Q3", "A_Q3", "1990-01-01", "111", "a_q3@t.com", "alice_q3", "pass")
    client_bob = client_service.register("Bob Q3", "B_Q3", "1991-02-02", "222", "b_q3@t.com", "bob_q3", "pass")
    client_charlie = client_service.register("Charlie Q3", "C_Q3", "1992-03-03", "333", "c_q3@t.com", "charlie_q3",
                                             "pass")
    client_dave = client_service.register("Dave Q3", "D_Q3", "1993-04-04", "444", "d_q3@t.com", "dave_q3",
                                          "pass")  # Несхвалений

    # 2. Схвалюємо деяких
    client_service.approve_registration(client_alice.key.id)
    client_service.approve_registration(client_bob.key.id)
    client_service.approve_registration(client_charlie.key.id)

    # 3. Створюємо типи абонементів
    pt_day = pass_type_service.add(name="Day Pass", limit_lifts=50, limit_hours=8, price=100)
    pt_10lift = pass_type_service.add(name="10-Lift Pass", limit_lifts=10, limit_hours=0, price=50)
    pt_season = pass_type_service.add(name="Season Pass", limit_lifts=999, limit_hours=999, price=1000)

    # 4. Створюємо абонементи (головні тестові дані)
    # Ми будемо тестувати період: 2025-10-26 - 2025-10-28

    # Поза періодом (До)
    pass_service.add(client_alice.id, pt_day.id, date(2025, 10, 25), date(2025, 10, 25), date(2025, 10, 25))

    # В періоді (День 1: 2025-10-26) - 2 продажі
    pass_service.add(client_bob.id, pt_day.id, date(2025, 10, 26), date(2025, 10, 26), date(2025, 10, 26))
    pass_service.add(client_charlie.id, pt_season.id, date(2025, 10, 26), date(2025, 10, 26), date(2026, 4, 1))

    # В періоді (День 2: 2025-10-27) - 2 продажі
    pass_service.add(client_bob.id, pt_10lift.id, date(2025, 10, 27), date(2025, 10, 27), date(2025, 11, 27))
    pass_service.add(client_alice.id, pt_day.id, date(2025, 10, 27), date(2025, 10, 27), date(2025, 10, 27))

    # В періоді (День 3: 2025-10-28) - 2 продажі
    pass_service.add(client_dave.id, pt_season.id, date(2025, 10, 28), date(2025, 10, 28),
                     date(2026, 4, 1))  # <-- Несхвалений клієнт
    pass_service.add(client_alice.id, pt_day.id, date(2025, 10, 28), date(2025, 10, 28), date(2025, 10, 28))

    # Поза періодом (Після)
    pass_service.add(client_bob.id, pt_10lift.id, date(2025, 10, 29), date(2025, 10, 29), date(2025, 11, 29))


# --- Тестовий клас для Запиту 3 ---

@pytest.fixture(scope="class")  # <- ЦЯ МОЖЕ ЗАЛИШИТИСЬ 'class', бо вона не залежить від БД
def report_3_dates():
    """Надає стандартизовані дати для тестів Запиту 3."""
    return {
        "start": date(2025, 10, 26),  # Перший день з продажами в тестовому періоді
        "mid": date(2025, 10, 27),
        "end": date(2025, 10, 28),  # Останній день з продажами в тестовому періоді
        "before": date(2025, 10, 25),  # День до тестового періоду
        "after": date(2025, 10, 29),  # День після тестового періоду
        "empty_start": date(2025, 1, 1),
        "empty_end": date(2025, 1, 7)
    }


@pytest.mark.usefixtures("populate_db_for_query3")
class TestReport3PassSales:
    """Групує всі тести для Запиту 3 (Продажі абонементів)."""

    def test_get_pass_sales_by_day_full_period(self, report_service, report_3_dates):
        """1. Тестує продажі за день за повний, багатоденний період."""
        # Arrange
        start, end = report_3_dates["start"], report_3_dates["end"]
        # Очікується: 26-го (2), 27-го (2), 28-го (2)

        # Act
        results = report_service.get_pass_sales_by_day(start, end)

        # Assert
        assert len(results) == 3
        counts = {r.purchase_date: r.sales_count for r in results}
        assert counts[date(2025, 10, 26)] == 2
        assert counts[date(2025, 10, 27)] == 2
        assert counts[date(2025, 10, 28)] == 2

    def test_get_pass_sales_by_type_full_period(self, report_service, report_3_dates):
        """2. Тестує продажі за типом за повний, багатоденний період."""
        # Arrange
        start, end = report_3_dates["start"], report_3_dates["end"]
        # Очікується: Day Pass (3), 10-Lift (1), Season (2)

        # Act
        results = report_service.get_pass_sales_by_type(start, end)

        # Assert
        assert len(results) == 3
        counts = {r.pass_type_name: r.sales_count for r in results}
        assert counts["Day Pass"] == 3
        assert counts["10-Lift Pass"] == 1
        assert counts["Season Pass"] == 2

    def test_get_pass_sales_by_day_single_day(self, report_service, report_3_dates):
        """3. Тестує продажі за день за період в один день."""
        # Arrange
        day = report_3_dates["mid"]  # 2025-10-27
        # Очікується: 27-го (2)

        # Act
        results = report_service.get_pass_sales_by_day(day, day)

        # Assert
        assert len(results) == 1
        assert results[0].purchase_date == day
        assert results[0].sales_count == 2

    def test_get_pass_sales_by_type_single_day(self, report_service, report_3_dates):
        """4. Тестує продажі за типом за період в один день."""
        # Arrange
        day = report_3_dates["mid"]  # 2025-10-27
        # Очікується: Day Pass (1), 10-Lift (1)

        # Act
        results = report_service.get_pass_sales_by_type(day, day)

        # Assert
        assert len(results) == 2
        counts = {r.pass_type_name: r.sales_count for r in results}
        assert counts["Day Pass"] == 1
        assert counts["10-Lift Pass"] == 1
        assert "Season Pass" not in counts

    def test_get_pass_sales_by_day_no_sales(self, report_service, report_3_dates):
        """5. Тестує продажі за день за період без продажів."""
        # Arrange
        start, end = report_3_dates["empty_start"], report_3_dates["empty_end"]

        # Act
        results = report_service.get_pass_sales_by_day(start, end)

        # Assert
        assert len(results) == 0

    def test_get_pass_sales_by_type_no_sales(self, report_service, report_3_dates):
        """6. Тестує продажі за типом за період без продажів."""
        # Arrange
        start, end = report_3_dates["empty_start"], report_3_dates["empty_end"]

        # Act
        results = report_service.get_pass_sales_by_type(start, end)

        # Assert
        assert len(results) == 0

    def test_get_pass_sales_period_misses_all(self, report_service, report_3_dates):
        """7. Тестує період, який є дійсним, але не містить даних (наприклад, між датами продажів)."""
        # Arrange
        start = date(2025, 10, 20)
        end = date(2025, 10, 24)

        # Act
        results_day = report_service.get_pass_sales_by_day(start, end)
        results_type = report_service.get_pass_sales_by_type(start, end)

        # Assert
        assert len(results_day) == 0
        assert len(results_type) == 0

    def test_get_pass_sales_handles_null_dates(self, report_service, report_3_dates):
        """8. Тестує, що обидві функції повертають порожні списки, якщо будь-яка з дат є None."""
        # Arrange
        valid_date = report_3_dates["end"]

        # Act
        results_d1 = report_service.get_pass_sales_by_day(None, valid_date)
        results_d2 = report_service.get_pass_sales_by_day(valid_date, None)
        results_d3 = report_service.get_pass_sales_by_day(None, None)

        results_t1 = report_service.get_pass_sales_by_type(None, valid_date)
        results_t2 = report_service.get_pass_sales_by_type(valid_date, None)
        results_t3 = report_service.get_pass_sales_by_type(None, None)

        # Assert
        assert results_d1 == []
        assert results_d2 == []
        assert results_d3 == []
        assert results_t1 == []
        assert results_t2 == []
        assert results_t3 == []

    def test_get_pass_sales_by_day_includes_start_boundary(self, report_service, report_3_dates):
        """9. Тестує продажі за день лише для першого дня періоду."""
        # Arrange
        day = report_3_dates["start"]  # 2025-10-26
        # Очікується: 26-го (2)

        # Act
        results = report_service.get_pass_sales_by_day(day, day)

        # Assert
        assert len(results) == 1
        assert results[0].purchase_date == day
        assert results[0].sales_count == 2

    def test_get_pass_sales_by_day_includes_end_boundary(self, report_service, report_3_dates):
        """10. Тестує продажі за день лише для останнього дня періоду."""
        # Arrange
        day = report_3_dates["end"]  # 2025-10-28
        # Очікується: 28-го (2)

        # Act
        results = report_service.get_pass_sales_by_day(day, day)

        # Assert
        assert len(results) == 1
        assert results[0].purchase_date == day
        assert results[0].sales_count == 2

    def test_pass_sales_includes_unapproved_client_pass(self, report_service, report_3_dates):
        """11. Підтверджує, що запит про продажі абонементів враховує абонементи несхвалених клієнтів."""
        # Arrange
        day = report_3_dates["end"]  # 2025-10-28
        # Очікується: Day Pass (1, Alice), Season Pass (1, Dave-unapproved)

        # Act
        results = report_service.get_pass_sales_by_type(day, day)

        # Assert
        # На відміну від Запиту 1, Запит 3 не повинен фільтрувати за схваленням.
        # Він рахує ВСІ продажі.
        assert len(results) == 2
        counts = {r.pass_type_name: r.sales_count for r in results}
        assert counts["Day Pass"] == 1
        assert counts["Season Pass"] == 1  # Цей абонемент належить 'dave'