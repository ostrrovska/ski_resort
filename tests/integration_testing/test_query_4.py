import pytest
from datetime import date, time
from models import db
from models.key import Key, AccessRight
from models.client import Client
from models.lift import Lift
from models.lift_usage import LiftUsage

# Імпортуємо сервіси, необхідні для налаштування даних та тестування
from services.client_service import ClientService
from services.lift_service import LiftService
from services.lift_usage_service import LiftUsageService
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


@pytest.fixture(scope='function')
def client_service():
    """Надає ClientService для створення тестових даних."""
    return ClientService()


@pytest.fixture(scope='function')
def lift_service():
    """Надає LiftService для створення тестових даних."""
    return LiftService()


@pytest.fixture(scope='function')
def lift_usage_service():
    """Надає LiftUsageService для створення тестових даних."""
    return LiftUsageService()


# --- Фікстура для наповнення БД даними ЛИШЕ для Запиту 4 ---

@pytest.fixture(scope='function')
def populate_db_for_query4(init_database, client_service, lift_service, lift_usage_service):
    """
    Наповнює БД даними, необхідними виключно для тестування звітів
    про використання підйомників (Запит 4).
    """

    # --- ЗМІНЕНО: Створюємо Client, а не Employee ---
    # 1. Створюємо клієнта (потрібен для lift_usage.client_id)
    test_user = client_service.register("Test User L4", "L4", "2000-01-01", "123", "test_l4@user.com", "user_l4",
                                        "pass")
    client_service.approve_registration(test_user.key.id)
    test_user_id = test_user.id
    # --- ---

    # 2. Створюємо підйомники
    lift_a = lift_service.add(name="Alpha", height=100)  # ID 1
    lift_b = lift_service.add(name="Bravo", height=200)  # ID 2
    lift_c = lift_service.add(name="Charlie", height=300)  # ID 3
    lift_d_unused = lift_service.add(name="Delta (Unused)", height=50)  # ID 4

    # 3. Створюємо тестові дати
    day_before = date(2025, 11, 9)
    day1 = date(2025, 11, 10)  # Понеділок
    day2 = date(2025, 11, 11)  # Вівторок
    day3 = date(2025, 11, 12)  # Середа
    day_after = date(2025, 11, 13)

    t1 = time(9, 0, 0)
    t2 = time(10, 0, 0)

    # 4. Створюємо використання підйомників
    # (Тепер test_user_id - це ID клієнта, і помилки не буде)
    lift_usage_service.add(test_user_id, lift_a.id, day_before, t1, t2)  # A: 1

    # В періоді (День 1: 2025-11-10)
    lift_usage_service.add(test_user_id, lift_a.id, day1, t1, t2)  # A: 2
    lift_usage_service.add(test_user_id, lift_a.id, day1, t1, t2)  # A: 3
    lift_usage_service.add(test_user_id, lift_b.id, day1, t1, t2)  # B: 1

    # В періоді (День 2: 2025-11-11)
    lift_usage_service.add(test_user_id, lift_b.id, day2, t1, t2)  # B: 2
    lift_usage_service.add(test_user_id, lift_b.id, day2, t1, t2)  # B: 3
    lift_usage_service.add(test_user_id, lift_b.id, day2, t1, t2)  # B: 4

    # В періоді (День 3: 2025-11-12)
    lift_usage_service.add(test_user_id, lift_c.id, day3, t1, t2)  # C: 1
    lift_usage_service.add(test_user_id, lift_c.id, day3, t1, t2)  # C: 2
    lift_usage_service.add(test_user_id, lift_c.id, day3, t1, t2)  # C: 3
    lift_usage_service.add(test_user_id, lift_c.id, day3, t1, t2)  # C: 4
    lift_usage_service.add(test_user_id, lift_a.id, day3, t1, t2)  # A: 4

    # Поза періодом (Після)
    lift_usage_service.add(test_user_id, lift_c.id, day_after, t1, t2)  # C: 5


# --- Тестовий клас для Запиту 4 ---

@pytest.fixture(scope="class")
def report_4_dates():
    """Надає стандартизовані дати для тестів Запиту 4."""
    return {
        "day1_start": date(2025, 11, 10),
        "day1_end": date(2025, 11, 10),
        "day2_start": date(2025, 11, 11),
        "day2_end": date(2025, 11, 11),
        "day3_start": date(2025, 11, 12),
        "day3_end": date(2025, 11, 12),

        "full_start": date(2025, 11, 10),  # Повний період (3 дні)
        "full_end": date(2025, 11, 12),

        "partial_start": date(2025, 11, 10),  # Частковий період (2 дні)
        "partial_end": date(2025, 11, 11),

        "outside_before": date(2025, 11, 9),
        "outside_after": date(2025, 11, 13),

        "empty_start": date(2025, 1, 1),
        "empty_end": date(2025, 1, 7)
    }


@pytest.mark.usefixtures("populate_db_for_query4")
class TestReport4LiftUsage:
    """Групує всі тести для Запиту 4 (Використання підйомників)."""

    def test_get_most_used_lifts_full_period(self, report_service, report_4_dates):
        """1. Тестує повний 3-денний період."""
        # Arrange
        start, end = report_4_dates["full_start"], report_4_dates["full_end"]
        # Очікується: Bravo (4), Charlie (4), Alpha (3)
        # (Сортування за алфавітом при однаковій кількості)

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 3  # 3 підйомники були використані
        assert results[0].lift_name == "Bravo"
        assert results[0].usage_count == 4
        assert results[1].lift_name == "Charlie"
        assert results[1].usage_count == 4
        assert results[2].lift_name == "Alpha"
        assert results[2].usage_count == 3

    def test_get_most_used_lifts_day_1_only(self, report_service, report_4_dates):
        """2. Тестує статистику лише за 'day1'."""
        # Arrange
        start, end = report_4_dates["day1_start"], report_4_dates["day1_end"]
        # Очікується: Alpha (2), Bravo (1)

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 2
        assert results[0].lift_name == "Alpha"
        assert results[0].usage_count == 2
        assert results[1].lift_name == "Bravo"
        assert results[1].usage_count == 1

    def test_get_most_used_lifts_day_2_only(self, report_service, report_4_dates):
        """3. Тестує статистику лише за 'day2' (лише один підйомник)."""
        # Arrange
        start, end = report_4_dates["day2_start"], report_4_dates["day2_end"]
        # Очікується: Bravo (3)

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 1
        assert results[0].lift_name == "Bravo"
        assert results[0].usage_count == 3

    def test_get_most_used_lifts_day_3_only(self, report_service, report_4_dates):
        """4. Тестує статистику лише за 'day3'."""
        # Arrange
        start, end = report_4_dates["day3_start"], report_4_dates["day3_end"]
        # Очікується: Charlie (4), Alpha (1)

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 2
        assert results[0].lift_name == "Charlie"
        assert results[0].usage_count == 4
        assert results[1].lift_name == "Alpha"
        assert results[1].usage_count == 1

    def test_get_most_used_lifts_partial_period(self, report_service, report_4_dates):
        """5. Тестує частковий період (day1 + day2)."""
        # Arrange
        start, end = report_4_dates["partial_start"], report_4_dates["partial_end"]
        # Очікується: Bravo (1 + 3 = 4), Alpha (2)

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 2
        assert results[0].lift_name == "Bravo"
        assert results[0].usage_count == 4
        assert results[1].lift_name == "Alpha"
        assert results[1].usage_count == 2

    def test_get_most_used_lifts_unused_lift_not_shown(self, report_service, report_4_dates):
        """6. Перевіряє, що невикористаний підйомник 'Delta' не з'являється у звіті."""
        # Arrange
        start, end = report_4_dates["full_start"], report_4_dates["full_end"]

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        lift_names = [r.lift_name for r in results]
        assert len(results) == 3
        assert "Delta (Unused)" not in lift_names

    def test_get_most_used_lifts_period_before_all(self, report_service, report_4_dates):
        """7. Тестує період до всіх основних даних (має бути порожнім)."""
        # Arrange
        start, end = report_4_dates["empty_start"], report_4_dates["empty_end"]

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 0

    def test_get_most_used_lifts_period_includes_only_before(self, report_service, report_4_dates):
        """8. Тестує період, який включає лише дані 'day_before'."""
        # Arrange
        start, end = report_4_dates["outside_before"], report_4_dates["outside_before"]
        # Очікується: Alpha (1)

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 1
        assert results[0].lift_name == "Alpha"
        assert results[0].usage_count == 1

    def test_get_most_used_lifts_period_includes_only_after(self, report_service, report_4_dates):
        """9. Тестує період, який включає лише дані 'day_after'."""
        # Arrange
        start, end = report_4_dates["outside_after"], report_4_dates["outside_after"]
        # Очікується: Charlie (1)

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 1
        assert results[0].lift_name == "Charlie"
        assert results[0].usage_count == 1

    def test_get_most_used_lifts_handles_null_dates(self, report_service, report_4_dates):
        """10. Тестує, що функція повертає [] якщо будь-яка з дат є None."""
        # Arrange
        valid_date = report_4_dates["full_end"]

        # Act
        results1 = report_service.get_most_used_lifts_by_period(None, valid_date)
        results2 = report_service.get_most_used_lifts_by_period(valid_date, None)
        results3 = report_service.get_most_used_lifts_by_period(None, None)

        # Assert
        assert results1 == []
        assert results2 == []
        assert results3 == []

    def test_get_most_used_lifts_period_spanning_all_data(self, report_service, report_4_dates):
        """11. Тестує дуже широкий період, що охоплює всі тестові дані."""
        # Arrange
        start, end = report_4_dates["outside_before"], report_4_dates["outside_after"]
        # Очікується:
        # Bravo (B): 4 (з day1, day2)
        # Charlie (C): 5 (4 з day3, 1 з day_after)
        # Alpha (A): 4 (1 з day_before, 2 з day1, 1 з day3)
        # Порядок: Charlie (5), Alpha (4), Bravo (4)

        # Act
        results = report_service.get_most_used_lifts_by_period(start, end)

        # Assert
        assert len(results) == 3
        assert results[0].lift_name == "Charlie"
        assert results[0].usage_count == 5
        assert results[1].lift_name == "Alpha"
        assert results[1].usage_count == 4
        assert results[2].lift_name == "Bravo"
        assert results[2].usage_count == 4