import pytest
from datetime import date, time
from models import db
from models.key import Key, AccessRight
from models.client import Client
from models.lift import Lift
from models.lift_usage import LiftUsage

# Import services
from services.client_service import ClientService
from services.lift_service import LiftService
from services.lift_usage_service import LiftUsageService
from services.report_service import ReportService

pytestmark = pytest.mark.usefixtures("app_context")


# --- Database Fixtures ---

@pytest.fixture(scope='function')
def init_database(app_context):
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


# --- Service Fixtures ---

@pytest.fixture(scope='function')
def report_service():
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


# --- Data Population Fixture ---

@pytest.fixture(scope='function')
def populate_db_for_query9(init_database, client_service, lift_service, lift_usage_service):
    """
    Populates the DB with data specifically for testing Query 9.
    """
    # 1. Create Clients
    c_alice = client_service.register("Alice Q9 (In, 3 visits)", "A_Q9", "1990-01-01", "111", "a_q9@t.com", "alice_q9",
                                      "pass")
    c_bob = client_service.register("Bob Q9 (Out, 5 visits)", "B_Q9", "1991-02-02", "222", "b_q9@t.com", "bob_q9",
                                    "pass")
    c_charlie = client_service.register("Charlie Q9 (In, 2 visits)", "C_Q9", "1992-03-03", "333", "c_q9@t.com",
                                        "charlie_q9", "pass")
    c_dave = client_service.register("Dave Q9 (Unapproved, 5 visits)", "D_Q9", "1993-04-04", "444", "d_q9@t.com",
                                     "dave_q9", "pass")

    # 2. Approve clients
    client_service.approve_registration(c_alice.key.id)
    client_service.approve_registration(c_bob.key.id)
    client_service.approve_registration(c_charlie.key.id)
    # Dave remains unapproved

    # 3. Create Lift
    lift1 = lift_service.add(name="Query 9 Lift", height=100)

    # 4. Create Dates
    t1, t2 = time(9, 0), time(10, 0)

    # Dates IN range [2025-01-02 to 2025-01-12]
    date_in_1 = date(2025, 1, 3)
    date_in_2 = date(2025, 1, 5)
    date_in_3 = date(2025, 1, 10)
    date_in_4 = date(2025, 1, 12)  # Boundary
    date_in_5 = date(2025, 1, 4)

    # Dates OUT of range
    date_out_1 = date(2025, 1, 1)  # Boundary
    date_out_2 = date(2025, 1, 15)
    date_out_3 = date(2025, 2, 1)
    date_out_4 = date(2025, 2, 2)
    date_out_5 = date(2025, 2, 3)

    # 5. Create LiftUsage

    # Client A (Alice): 3 visits, ALL in range
    lift_usage_service.add(c_alice.id, lift1.id, date_in_1, t1, t2)
    lift_usage_service.add(c_alice.id, lift1.id, date_in_2, t1, t2)
    lift_usage_service.add(c_alice.id, lift1.id, date_in_3, t1, t2)

    # Client B (Bob): 5 visits, NONE in range
    lift_usage_service.add(c_bob.id, lift1.id, date_out_1, t1, t2)
    lift_usage_service.add(c_bob.id, lift1.id, date_out_2, t1, t2)
    lift_usage_service.add(c_bob.id, lift1.id, date_out_3, t1, t2)
    lift_usage_service.add(c_bob.id, lift1.id, date_out_4, t1, t2)
    lift_usage_service.add(c_bob.id, lift1.id, date_out_5, t1, t2)

    # Client C (Charlie): 2 visits, ALL in range (but one day has 10 usages)
    for _ in range(10):  # 10 usages on one day
        lift_usage_service.add(c_charlie.id, lift1.id, date_in_5, t1, t2)
    lift_usage_service.add(c_charlie.id, lift1.id, date_in_4, t1, t2)  # 1 usage on another day

    # Client D (Dave - Unapproved): 5 visits, 2 in range
    lift_usage_service.add(c_dave.id, lift1.id, date_in_1, t1, t2)
    lift_usage_service.add(c_dave.id, lift1.id, date_in_2, t1, t2)
    lift_usage_service.add(c_dave.id, lift1.id, date_out_3, t1, t2)
    lift_usage_service.add(c_dave.id, lift1.id, date_out_4, t1, t2)
    lift_usage_service.add(c_dave.id, lift1.id, date_out_5, t1, t2)

    return {
        "c_alice_id": c_alice.id,
        "c_bob_id": c_bob.id,
        "c_charlie_id": c_charlie.id,
        "c_dave_id": c_dave.id,
        "range_start": date(2025, 1, 2),
        "range_end": date(2025, 1, 12),
        "threshold": 3
    }


# --- Test Class ---

@pytest.mark.usefixtures("populate_db_for_query9")
class TestReport9ClientVisits:

    def test_get_clients_visited_in_date_range(self, report_service, populate_db_for_query9):
        """
        Tests Part 1: Clients who visited between Jan 2 and Jan 12.
        """
        # Arrange
        start_date = populate_db_for_query9["range_start"]
        end_date = populate_db_for_query9["range_end"]

        # Expected: Alice (visited 3, 5, 10), Charlie (visited 4, 12)
        # Not Expected: Bob (no visits in range), Dave (unapproved)

        # Act
        results = report_service.get_clients_visited_in_date_range(start_date, end_date)

        # Assert
        assert len(results) == 2
        client_ids = [r.id for r in results]

        assert populate_db_for_query9["c_alice_id"] in client_ids
        assert populate_db_for_query9["c_charlie_id"] in client_ids

        assert populate_db_for_query9["c_bob_id"] not in client_ids
        assert populate_db_for_query9["c_dave_id"] not in client_ids

    def test_get_clients_visited_more_than_x_times(self, report_service, populate_db_for_query9):
        """
        Tests Part 2: Clients who visited > 3 times (distinct days).
        """
        # Arrange
        threshold = populate_db_for_query9["threshold"]

        # Expected: Bob (5 distinct visits)
        # Not Expected: Alice (3 visits), Charlie (2 distinct visits), Dave (unapproved, 5 visits)

        # Act
        results = report_service.get_clients_visited_more_than_x_times(threshold)

        # Assert
        assert len(results) == 1

        client_result, visit_count = results[0]

        assert client_result.id == populate_db_for_query9["c_bob_id"]
        assert visit_count == 5

    def test_get_clients_visited_in_date_range_no_results(self, report_service, populate_db_for_query9):
        """Tests date range with no visits."""
        # Arrange
        start_date = date(2026, 1, 1)
        end_date = date(2026, 1, 31)

        # Act
        results = report_service.get_clients_visited_in_date_range(start_date, end_date)

        # Assert
        assert len(results) == 0

    def test_get_clients_visited_more_than_x_times_no_results(self, report_service, populate_db_for_query9):
        """Tests visit threshold that no one meets."""
        # Arrange
        threshold = 10

        # Act
        results = report_service.get_clients_visited_more_than_x_times(threshold)

        # Assert
        assert len(results) == 0

    def test_services_handle_none_params(self, report_service):
        """Tests that services gracefully handle None inputs."""
        # Act
        results_range = report_service.get_clients_visited_in_date_range(None, None)
        results_freq = report_service.get_clients_visited_more_than_x_times(None)

        # Assert
        assert results_range == []
        assert results_freq == []