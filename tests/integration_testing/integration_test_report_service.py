import pytest
from datetime import date, time, timedelta
from models import db
from models.key import AccessRight

# Import services needed to set up the data
from services.client_service import ClientService
from services.employee_service import EmployeeService
from services.pass_type_service import PassTypeService
from services.pass_service import PassService
from services.equipment_type_service import EquipmentTypeService
from services.equipment_service import EquipmentService
from services.rental_service import RentalService
from services.rental_equipment_service import RentalEquipmentService

# Import the service being TESTED
from services.report_service import ReportService

# Automatically apply the app_context fixture to all tests in this file
pytestmark = pytest.mark.usefixtures("app_context")


# --- Database Fixtures ---

@pytest.fixture(scope='function')
def init_database(app_context):
    """Creates all tables in memory before a test and drops them after."""
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def report_service():
    """Provides an instance of the service being tested."""
    return ReportService()


@pytest.fixture(scope='function')
def populate_db(init_database):
    """
    Populates the in-memory database with a complex set of test data
    to cover scenarios for both reports, including edge cases.
    """
    # Create services for setup
    client_service = ClientService()
    pass_type_service = PassTypeService()
    pass_service = PassService()
    employee_service = EmployeeService()
    eq_type_service = EquipmentTypeService()
    eq_service = EquipmentService()
    rental_service = RentalService()
    rental_eq_service = RentalEquipmentService()

    # --- Data for Report 1 (Clients and Passes) ---

    # 1. Create Clients
    client_alice = client_service.register("Alice Smith", "AS123", "1990-05-15", "111", "alice@a.com", "alice", "pass")
    client_bob = client_service.register("Bob Johnson", "BJ456", "1985-02-20", "222", "bob@b.com", "bob", "pass")
    client_charlie = client_service.register("Charlie Day", "CD789", "1995-10-30", "333", "charlie@c.com", "charlie",
                                             "pass")
    client_dave = client_service.register("Dave R", "DR111", "1992-01-01", "444", "dave@d.com", "dave",
                                          "pass")  # Stays unapproved

    # 2. Approve clients (except Dave)
    client_service.approve_registration(client_alice.key.id)
    client_service.approve_registration(client_bob.key.id)
    client_service.approve_registration(client_charlie.key.id)
    # client_dave remains pending

    # 3. Create Pass Types
    pt_day = pass_type_service.add(name="Day Pass", limit_lifts=50, limit_hours=8, price=100)
    pt_10lift = pass_type_service.add(name="10-Lift Pass", limit_lifts=10, limit_hours=0, price=50)
    pt_season = pass_type_service.add(name="Season Pass", limit_lifts=999, limit_hours=999, price=1000)

    # 4. Create Passes
    pass_alice_1 = pass_service.add(client_alice.id, pt_day.id, date(2025, 10, 25), date(2025, 10, 25),
                                    date(2025, 10, 25))
    pass_bob_1 = pass_service.add(client_bob.id, pt_day.id, date(2025, 10, 26), date(2025, 10, 26), date(2025, 10, 26))
    pass_bob_2 = pass_service.add(client_bob.id, pt_10lift.id, date(2025, 10, 27), date(2025, 10, 27),
                                  date(2025, 11, 27))
    # client_charlie has no passes
    pass_dave_1 = pass_service.add(client_dave.id, pt_season.id, date(2025, 10, 28), date(2025, 10, 28),
                                   date(2026, 4, 1))

    # --- Data for Report 2 (Equipment Rentals) ---

    # 1. Create Employee
    emp_rick = employee_service.add("Rick Rental", "Rental Staff", 30000, "555", "rick@r.com")

    # 2. Create Equipment Types
    eq_type_skis = eq_type_service.add("Skis", "For skiing")
    eq_type_board = eq_type_service.add("Snowboard", "For snowboarding")
    eq_type_poles = eq_type_service.add("Poles", "For balance")  # Rented 1 time

    # 3. Create Equipment
    eq_atomic = eq_service.add(eq_type_skis.id, "Atomic Redster", True)  # ID 1
    eq_burton = eq_service.add(eq_type_board.id, "Burton Custom", True)  # ID 2
    eq_rossignol = eq_service.add(eq_type_skis.id, "Rossignol Hero", True)  # ID 3
    eq_leki = eq_service.add(eq_type_poles.id, "Leki Poles", True)  # ID 4

    # 4. Define Test Dates
    test_day = date(2025, 10, 27)
    test_day_single_type = date(2025, 10, 30)
    test_week_start = date(2025, 10, 27)
    test_week_end = test_week_start + timedelta(days=6)  # 2025-11-02
    day_before_week = test_week_start - timedelta(days=1)  # 2025-10-26
    day_after_week = test_week_end + timedelta(days=1)  # 2025-11-03

    # 5. Create Rentals and Links

    # Rentals on "test_day" (2025-10-27) - Start of week
    # Expected: 1 Skis (Atomic), 2 Snowboard (Burton, Burton)
    rent_1 = rental_service.add(client_alice.id, emp_rick.id, test_day, time(9, 0), time(17, 0), "daily", 100)
    rental_eq_service.add(rent_1.id, eq_atomic.id)  # Atomic (1)

    rent_2 = rental_service.add(client_bob.id, emp_rick.id, test_day, time(9, 5), time(17, 5), "daily", 120)
    rental_eq_service.add(rent_2.id, eq_burton.id)  # Burton (1)

    rent_3 = rental_service.add(client_charlie.id, emp_rick.id, test_day, time(9, 10), time(17, 10), "daily", 120)
    rental_eq_service.add(rent_3.id, eq_burton.id)  # Burton (2)

    # Rentals mid-week (2025-10-29)
    rent_4_date = test_week_start + timedelta(days=2)
    rent_4 = rental_service.add(client_alice.id, emp_rick.id, rent_4_date, time(10, 0), time(18, 0), "daily", 100)
    rental_eq_service.add(rent_4.id, eq_atomic.id)  # Atomic (2)

    rent_5 = rental_service.add(client_bob.id, emp_rick.id, rent_4_date, time(10, 5), time(18, 5), "daily", 100)
    rental_eq_service.add(rent_5.id, eq_atomic.id)  # Atomic (3)

    rent_6 = rental_service.add(client_charlie.id, emp_rick.id, rent_4_date, time(10, 10), time(18, 10), "daily", 100)
    rental_eq_service.add(rent_6.id, eq_rossignol.id)  # Rossignol (1)

    # Rental on "test_day_single_type" (2025-10-30)
    # Expected: 1 Poles (Leki)
    rent_s = rental_service.add(client_alice.id, emp_rick.id, test_day_single_type, time(11, 0), time(12, 0), "hourly",
                                20)
    rental_eq_service.add(rent_s.id, eq_leki.id)  # Leki (1)

    # Rental on "test_week_end" (2025-11-02) - Boundary test
    rent_7 = rental_service.add(client_dave.id, emp_rick.id, test_week_end, time(14, 0), time(16, 0), "hourly", 240)
    rental_eq_service.add(rent_7.id, eq_burton.id)  # Burton (3) - Rented by unapproved client

    # Rental OUTSIDE week (2025-10-26) - Ignored by weekly report
    rent_8 = rental_service.add(client_alice.id, emp_rick.id, day_before_week, time(9, 0), time(17, 0), "daily", 100)
    rental_eq_service.add(rent_8.id, eq_atomic.id)

    # Rental OUTSIDE week (2025-11-03) - Ignored by weekly report
    rent_9 = rental_service.add(client_bob.id, emp_rick.id, day_after_week, time(9, 0), time(17, 0), "daily", 100)
    rental_eq_service.add(rent_9.id, eq_burton.id)

    # --- Weekly Summary (2025-10-27 to 2025-11-02) ---
    # eq_atomic (ID 1): 3 times (rent_1, rent_4, rent_5)
    # eq_burton (ID 2): 3 times (rent_2, rent_3, rent_7)
    # eq_rossignol (ID 3): 1 time (rent_6)
    # eq_leki (ID 4): 1 time (rent_s)
    # TIE between Atomic and Burton.

    # Return IDs for use in tests
    return {
        "client_alice_id": client_alice.id,
        "client_bob_id": client_bob.id,
        "client_charlie_id": client_charlie.id,
        "client_dave_id": client_dave.id,
        "pass_alice_1_id": pass_alice_1.id,
        "pass_bob_1_id": pass_bob_1.id,
        "pass_bob_2_id": pass_bob_2.id,
        "pass_dave_1_id": pass_dave_1.id,
        "eq_atomic_id": eq_atomic.id,
        "eq_burton_id": eq_burton.id,
        "eq_rossignol_id": eq_rossignol.id,
        "eq_leki_id": eq_leki.id,
        "test_day": test_day,
        "test_day_single_type": test_day_single_type,
        "test_week_start": test_week_start,
        "test_week_end": test_week_end,
        "day_before_week": day_before_week,
        "day_after_week": day_after_week,
    }


# --- Tests for Report 1: get_clients_and_passes ---

def test_get_clients_and_passes_success(report_service, populate_db):
    """
    Tests that the report correctly returns all approved clients who have passes.
    """
    # Act
    results = report_service.get_clients_and_passes()

    # Assert
    # 1. Check count: 3 passes (1 for Alice, 2 for Bob). Dave's pass is ignored.
    assert len(results) == 3

    # 2. Check that Charlie (no passes) and Dave (unapproved) are absent.
    client_ids = [row.client_id for row in results]
    assert populate_db["client_alice_id"] in client_ids
    assert populate_db["client_bob_id"] in client_ids
    assert populate_db["client_charlie_id"] not in client_ids
    assert populate_db["client_dave_id"] not in client_ids

    # 3. Check data for one row (Bob's 10-Lift Pass)
    bob_pass_2 = next((row for row in results if row.pass_id == populate_db["pass_bob_2_id"]), None)
    assert bob_pass_2 is not None
    assert bob_pass_2.full_name == "Bob Johnson"
    assert bob_pass_2.pass_type_name == "10-Lift Pass"
    assert bob_pass_2.remaining_lifts == 10


def test_get_clients_and_passes_sorting(report_service, populate_db):
    """
    Tests that the results are correctly sorted by client name, then purchase date.
    """
    # Act
    results = report_service.get_clients_and_passes()

    # Assert
    assert len(results) == 3
    # 1. Alice (ID 1) comes before Bob (ID 2)
    assert results[0].client_id == populate_db["client_alice_id"]
    assert results[1].client_id == populate_db["client_bob_id"]
    assert results[2].client_id == populate_db["client_bob_id"]

    # 2. Check Bob's passes are sorted by purchase_date
    assert results[1].pass_id == populate_db["pass_bob_1_id"]
    assert results[2].pass_id == populate_db["pass_bob_2_id"]
    assert results[1].purchase_date < results[2].purchase_date


def test_get_clients_and_passes_no_data(report_service, init_database):
    """
    Tests that the report returns an empty list if the DB has no passes.
    """
    # Act (use 'init_database' for an empty DB)
    results = report_service.get_clients_and_passes()

    # Assert
    assert len(results) == 0
    assert results == []


def test_get_clients_and_passes_ignores_unapproved_clients(report_service, populate_db):
    """
    Tests that passes belonging to unapproved clients are not included.
    """
    # Act
    results = report_service.get_clients_and_passes()

    # Assert
    pass_ids = [row.pass_id for row in results]
    assert populate_db["pass_dave_1_id"] not in pass_ids
    assert len(results) == 3  # Only Alice's and Bob's passes


# --- Tests for Report 2 (Daily): get_equipment_count_by_type_daily ---

def test_get_equipment_count_by_type_daily_success(report_service, populate_db):
    """
    Tests the daily count for a day with multiple rentals of multiple types.
    """
    # Arrange
    test_day = populate_db["test_day"]  # 2025-10-27
    # Expected: 1 Skis (Atomic), 2 Snowboard (Burton, Burton)

    # Act
    results = report_service.get_equipment_count_by_type_daily(test_day)

    # Assert
    assert len(results) == 2  # 2 types: Skis, Snowboard

    counts = {row.type_name: row.rental_count for row in results}
    assert "Skis" in counts
    assert counts["Skis"] == 1
    assert "Snowboard" in counts
    assert counts["Snowboard"] == 2


def test_get_equipment_count_by_type_daily_single_type(report_service, populate_db):
    """
    Tests the daily count for a day with rentals of only one type.
    """
    # Arrange
    test_day = populate_db["test_day_single_type"]  # 2025-10-30
    # Expected: 1 Poles (Leki)

    # Act
    results = report_service.get_equipment_count_by_type_daily(test_day)

    # Assert
    assert len(results) == 1
    assert results[0].type_name == "Poles"
    assert results[0].rental_count == 1


def test_get_equipment_count_by_type_daily_no_rentals(report_service, populate_db):
    """
    Tests the daily count for a day with no rentals.
    """
    # Arrange
    empty_day = date(2025, 1, 1)

    # Act
    results = report_service.get_equipment_count_by_type_daily(empty_day)

    # Assert
    assert len(results) == 0
    assert results == []


def test_get_equipment_count_by_type_daily_handles_none(report_service, populate_db):
    """
    Tests that the service handles None input gracefully.
    """
    # Act
    results = report_service.get_equipment_count_by_type_daily(None)

    # Assert
    assert len(results) == 0
    assert results == []


def test_get_equipment_count_by_type_daily_rentals_outside_day(report_service, populate_db):
    """
    Tests that rentals from other days are not included.
    """
    # Arrange
    day_before = populate_db["day_before_week"]  # 2025-10-26, has 1 Atomic rental

    # Act
    results = report_service.get_equipment_count_by_type_daily(day_before)

    # Assert
    assert len(results) == 1
    assert results[0].type_name == "Skis"
    assert results[0].rental_count == 1


# --- Tests for Report 2 (Weekly): get_most_rented_equipment_weekly ---

def test_get_most_rented_equipment_weekly_success_and_tie_order(report_service, populate_db):
    """
    Tests the weekly report for a full period, including boundary dates
    and correct sorting, especially in a tie.
    """
    # Arrange
    start_date = populate_db["test_week_start"]  # 2025-10-27
    end_date = populate_db["test_week_end"]  # 2025-11-02
    # Expected:
    # Atomic (ID 1): 3 times
    # Burton (ID 2): 3 times
    # Leki (ID 4): 1 time
    # Rossignol (ID 3): 1 time
    # (rent_8 and rent_9 are ignored)

    # Act
    results = report_service.get_most_rented_equipment_weekly(start_date, end_date)

    # Assert
    assert len(results) == 4

    # 1. Check counts and primary sort order (descending count)
    assert results[0].rental_count == 3
    assert results[1].rental_count == 3
    assert results[2].rental_count == 1
    assert results[3].rental_count == 1

    # 2. Check tie-breaking sort (alphabetical by model)
    # "Atomic Redster" (ID 1) should come before "Burton Custom" (ID 2)
    assert results[0].id == populate_db["eq_atomic_id"]
    assert results[1].id == populate_db["eq_burton_id"]

    # "Leki Poles" (ID 4) should come before "Rossignol Hero" (ID 3)
    assert results[2].id == populate_db["eq_leki_id"]
    assert results[3].id == populate_db["eq_rossignol_id"]


def test_get_most_rented_equipment_weekly_no_rentals(report_service, populate_db):
    """
    Tests the weekly report for a date range with no rentals.
    """
    # Arrange
    empty_week_start = date(2025, 1, 1)
    empty_week_end = date(2025, 1, 7)

    # Act
    results = report_service.get_most_rented_equipment_weekly(empty_week_start, empty_week_end)

    # Assert
    assert len(results) == 0
    assert results == []


def test_get_most_rented_equipment_weekly_handles_empty_dates(report_service, populate_db):
    """
    Tests that the service gracefully handles None inputs for dates.
    """
    # Act
    results_none_all = report_service.get_most_rented_equipment_weekly(None, None)
    results_none_start = report_service.get_most_rented_equipment_weekly(None, populate_db["test_week_end"])
    results_none_end = report_service.get_most_rented_equipment_weekly(populate_db["test_week_start"], None)

    # Assert
    assert results_none_all == []
    assert results_none_start == []
    assert results_none_end == []


def test_get_most_rented_equipment_weekly_single_day_period(report_service, populate_db):
    """
    Tests the weekly report when the start and end date are the same.
    """
    # Arrange
    test_day = populate_db["test_day"]  # 2025-10-27
    # Expected: Burton (2), Atomic (1)

    # Act
    results = report_service.get_most_rented_equipment_weekly(test_day, test_day)

    # Assert
    assert len(results) == 2
    # 1. Check counts and order
    assert results[0].id == populate_db["eq_burton_id"]
    assert results[0].rental_count == 2
    assert results[1].id == populate_db["eq_atomic_id"]
    assert results[1].rental_count == 1


def test_get_most_rented_equipment_weekly_partial_overlap(report_service, populate_db):
    """
    Tests a period that only catches some of the rentals.
    """
    # Arrange
    start_date = populate_db["test_week_end"]  # 2025-11-02
    end_date = populate_db["day_after_week"]  # 2025-11-03
    # Expected: Burton (1 from 11-02), Burton (1 from 11-03)
    # The query groups by equipment ID, so it should be:
    # Burton (ID 2): 2 times

    # Act
    results = report_service.get_most_rented_equipment_weekly(start_date, end_date)

    # Assert
    assert len(results) == 1
    assert results[0].id == populate_db["eq_burton_id"]
    assert results[0].model == "Burton Custom"
    assert results[0].rental_count == 2


def test_get_most_rented_equipment_weekly_includes_unapproved_client_rentals(report_service, populate_db):
    """
    Tests that rentals from unapproved clients are still counted,
    as the report is about equipment, not clients.
    """
    # Arrange
    start_date = populate_db["test_week_start"]  # 2025-10-27
    end_date = populate_db["test_week_end"]  # 2025-11-02
    # rent_7 (Burton) was by client_dave (unapproved) on 2025-11-02

    # Act
    results = report_service.get_most_rented_equipment_weekly(start_date, end_date)

    # Assert
    # Find the Burton result
    burton_result = next((row for row in results if row.id == populate_db["eq_burton_id"]), None)
    assert burton_result is not None
    # Check that its count is 3 (rent_2, rent_3, rent_7)
    assert burton_result.rental_count == 3