import pytest
from datetime import date, time
from models import db

# Імпортуємо сервіси, необхідні для налаштування
from services.client_service import ClientService
from services.employee_service import EmployeeService
from services.rental_service import RentalService

# Імпортуємо сервіс, що тестується
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


@pytest.fixture(scope='function')
def report_service():
    """Надає екземпляр сервісу, що тестується."""
    return ReportService()


# --- START: Додані відсутні фікстури ---
@pytest.fixture(scope='function')
def client_service():
    """Надає ClientService для створення тестових даних."""
    return ClientService()


@pytest.fixture(scope='function')
def employee_service():
    """Надає EmployeeService для створення тестових даних."""
    return EmployeeService()


@pytest.fixture(scope='function')
def rental_service():
    """Надає RentalService для створення тестових даних."""
    return RentalService()


# --- END: Додані відсутні фікстури ---


# --- Фікстура для наповнення БД даними ЛИШЕ для Запиту 5 ---

@pytest.fixture(scope='function')
def populate_db_for_query5(init_database, client_service, employee_service, rental_service):
    """
    Наповнює БД даними, необхідними виключно для тестування звітів
    про доходи від оренди (Запит 5).
    """
    # 1. Створюємо клієнта
    client = client_service.register("Client Q5", "C_Q5", "1990-01-01", "111", "c_q5@t.com", "client_q5", "pass")
    client_service.approve_registration(client.key.id)

    # 2. Створюємо працівника
    employee = employee_service.add("Employee Q5", "Staff", 30000, "222", "e_q5@t.com")

    # 3. Створюємо оренди (головні тестові дані)
    t1 = time(9, 0)
    t2 = time(10, 0)

    # --- 2024 (поза тестовим періодом) ---
    rental_service.add(client.id, employee.id, date(2024, 12, 31), t1, t2, "daily", 1000)

    # --- 2025 Q1 ---
    # 2025-01 (Jan)
    rental_service.add(client.id, employee.id, date(2025, 1, 15), t1, t2, "daily", 100)
    rental_service.add(client.id, employee.id, date(2025, 1, 20), t1, t2, "hourly", 50)
    # Jan Total: 150

    # 2025-03 (Mar)
    rental_service.add(client.id, employee.id, date(2025, 3, 10), t1, t2, "daily", 200)
    # Mar Total: 200
    # Q1 Total: 350

    # --- 2025 Q2 ---
    # 2025-04 (Apr)
    rental_service.add(client.id, employee.id, date(2025, 4, 5), t1, t2, "daily", 300)
    # Apr Total: 300

    # 2025-05 (May)
    rental_service.add(client.id, employee.id, date(2025, 5, 1), t1, t2, "daily", 10)
    rental_service.add(client.id, employee.id, date(2025, 5, 30), t1, t2, "daily", 15)
    # May Total: 25
    # Q2 Total: 325

    # --- 2025 Q4 ---
    # 2025-10 (Oct)
    rental_service.add(client.id, employee.id, date(2025, 10, 10), t1, t2, "daily", 500)
    # Oct Total: 500
    # Q4 Total: 500

    # --- 2026 (поза тестовим періодом) ---
    rental_service.add(client.id, employee.id, date(2026, 1, 1), t1, t2, "daily", 2000)

    return {
        "start_2025": date(2025, 1, 1),
        "end_2025": date(2025, 12, 31),
        "start_q1": date(2025, 1, 1),
        "end_q1": date(2025, 3, 31),
        "start_q2": date(2025, 4, 1),
        "end_q2": date(2025, 6, 30),
        "empty_start": date(2023, 1, 1),
        "empty_end": date(2023, 12, 31),
    }


@pytest.mark.usefixtures("populate_db_for_query5")
class TestReport5RentalRevenue:
    """Групує всі тести для Запиту 5 (Доходи від оренди)."""

    def test_get_rental_revenue_by_month_full_year(self, report_service, populate_db_for_query5):
        """1. Тестує місячний звіт за весь 2025 рік."""
        # Arrange
        start, end = populate_db_for_query5["start_2025"], populate_db_for_query5["end_2025"]

        # Act
        results = report_service.get_rental_revenue_by_month(start, end)

        # Assert
        assert len(results) == 5  # Jan, Mar, Apr, May, Oct
        counts = {r.month: r.total_revenue for r in results}

        assert counts[1] == 150  # Jan
        assert counts[3] == 200  # Mar
        assert counts[4] == 300  # Apr
        assert counts[5] == 25  # May
        assert counts[10] == 500  # Oct
        assert 12 not in counts  # Dec 2024
        assert 2 not in counts  # Feb 2025

    def test_get_rental_revenue_by_quarter_full_year(self, report_service, populate_db_for_query5):
        """2. Тестує квартальний звіт за весь 2025 рік."""
        # Arrange
        start, end = populate_db_for_query5["start_2025"], populate_db_for_query5["end_2025"]

        # Act
        results = report_service.get_rental_revenue_by_quarter(start, end)

        # Assert
        assert len(results) == 3  # Q1, Q2, Q4
        counts = {r.quarter: r.total_revenue for r in results}

        assert counts[1] == 350  # Q1 (150 + 200)
        assert counts[2] == 325  # Q2 (300 + 25)
        assert counts[4] == 500  # Q4 (500)
        assert 3 not in counts  # Q3

    def test_get_rental_revenue_by_month_q1_only(self, report_service, populate_db_for_query5):
        """3. Тестує місячний звіт лише за Q1."""
        # Arrange
        start, end = populate_db_for_query5["start_q1"], populate_db_for_query5["end_q1"]

        # Act
        results = report_service.get_rental_revenue_by_month(start, end)

        # Assert
        assert len(results) == 2  # Jan, Mar
        counts = {r.month: r.total_revenue for r in results}
        assert counts[1] == 150  # Jan
        assert counts[3] == 200  # Mar

    def test_get_rental_revenue_by_quarter_q2_only(self, report_service, populate_db_for_query5):
        """4. Тестує квартальний звіт лише за Q2."""
        # Arrange
        start, end = populate_db_for_query5["start_q2"], populate_db_for_query5["end_q2"]

        # Act
        results = report_service.get_rental_revenue_by_quarter(start, end)

        # Assert
        assert len(results) == 1  # Q2
        assert results[0].quarter == 2
        assert results[0].total_revenue == 325

    def test_get_rental_revenue_no_data(self, report_service, populate_db_for_query5):
        """5. Тестує період без даних (2023 рік)."""
        # Arrange
        start, end = populate_db_for_query5["empty_start"], populate_db_for_query5["empty_end"]

        # Act
        results_month = report_service.get_rental_revenue_by_month(start, end)
        results_quarter = report_service.get_rental_revenue_by_quarter(start, end)

        # Assert
        assert len(results_month) == 0
        assert len(results_quarter) == 0

    def test_get_rental_revenue_handles_null_dates(self, report_service, populate_db_for_query5):
        """6. Тестує, що функції повертають [] якщо дати None."""
        # Arrange
        valid_date = populate_db_for_query5["end_2025"]

        # Act
        results_m1 = report_service.get_rental_revenue_by_month(None, valid_date)
        results_m2 = report_service.get_rental_revenue_by_month(valid_date, None)
        results_m3 = report_service.get_rental_revenue_by_month(None, None)

        results_q1 = report_service.get_rental_revenue_by_quarter(None, valid_date)
        results_q2 = report_service.get_rental_revenue_by_quarter(valid_date, None)
        results_q3 = report_service.get_rental_revenue_by_quarter(None, None)

        # Assert
        assert results_m1 == []
        assert results_m2 == []
        assert results_m3 == []
        assert results_q1 == []
        assert results_q2 == []
        assert results_q3 == []