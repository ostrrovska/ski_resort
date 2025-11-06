import pytest
from datetime import date, time
from models import db

# Import services
from services.client_service import ClientService
from services.employee_service import EmployeeService
from services.schedule_service import ScheduleService
from services.equipment_type_service import EquipmentTypeService
from services.equipment_service import EquipmentService
from services.rental_service import RentalService
from services.rental_equipment_service import RentalEquipmentService
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
def employee_service():
    return EmployeeService()


@pytest.fixture(scope='function')
def schedule_service():
    return ScheduleService()


@pytest.fixture(scope='function')
def equipment_type_service():
    return EquipmentTypeService()


@pytest.fixture(scope='function')
def equipment_service():
    return EquipmentService()


@pytest.fixture(scope='function')
def rental_service():
    return RentalService()


@pytest.fixture(scope='function')
def rental_equipment_service():
    return RentalEquipmentService()


# --- Data Population Fixture ---

@pytest.fixture(scope='function')
def populate_db_for_query10(init_database, client_service, employee_service, schedule_service,
                            equipment_type_service, equipment_service, rental_service, rental_equipment_service):
    """
    Populates the DB with data specifically for testing Query 10.
    """
    # 1. Create Employees
    emp_alice = employee_service.add("Alice Q10", "Rental Staff", 30000, "111", "a_q10@t.com")
    emp_bob = employee_service.add("Bob Q10", "Manager", 50000, "222", "b_q10@t.com")
    emp_charlie = employee_service.add("Charlie Q10", "Rental Staff", 30000, "333",
                                       "c_q10@t.com")  # Works, but no rentals

    # 2. Create Client
    client1 = client_service.register("Client Q10", "C_Q10", "2000-01-01", "999", "c_q10@t.com", "client_q10", "pass")
    client_service.approve_registration(client1.key.id)

    # 3. Create Equipment
    et_skis = equipment_type_service.add("Skis", "For skiing")
    et_board = equipment_type_service.add("Snowboard", "For boarding")
    eq_skis = equipment_service.add(et_skis.id, "Atomic Skis", True)
    eq_board = equipment_service.add(et_board.id, "Burton Board", True)

    # 4. Create Dates
    t1_start, t1_end = time(9, 0), time(17, 0)
    t2_start, t2_end = time(10, 0), time(18, 0)

    test_day = date(2025, 11, 15)
    other_day = date(2025, 11, 16)

    # 5. Create Schedules
    schedule_service.add(emp_alice.id, test_day, t1_start, t1_end)
    schedule_service.add(emp_bob.id, other_day, t1_start, t1_end)
    schedule_service.add(emp_charlie.id, test_day, t2_start, t2_end)

    # 6. Create Rentals
    # Alice issues 2 items on test_day
    rent1 = rental_service.add(client1.id, emp_alice.id, test_day, t1_start, t1_end, "daily", 100)
    rental_equipment_service.add(rent1.id, eq_skis.id)

    rent2 = rental_service.add(client1.id, emp_alice.id, test_day, t1_start, t1_end, "daily", 150)
    rental_equipment_service.add(rent2.id, eq_board.id)

    # Bob issues 1 item on other_day
    rent3 = rental_service.add(client1.id, emp_bob.id, other_day, t1_start, t1_end, "daily", 100)
    rental_equipment_service.add(rent3.id, eq_skis.id)

    return {
        "emp_alice_id": emp_alice.id,
        "emp_bob_id": emp_bob.id,
        "emp_charlie_id": emp_charlie.id,
        "test_day": test_day,
        "other_day": other_day,
        "empty_day": date(2025, 1, 1)
    }


# --- Test Class ---

@pytest.mark.usefixtures("populate_db_for_query10")
class TestReport10EmployeeStats:

    def test_get_employees_working_on_date_success(self, report_service, populate_db_for_query10):
        """Tests Part 2: Get employees working on 'test_day'."""
        # Arrange
        test_day = populate_db_for_query10["test_day"]
        # Expected: Alice, Charlie

        # Act
        results = report_service.get_employees_working_on_date(test_day)

        # Assert
        assert len(results) == 2
        emp_ids = [emp.id for emp, start, end in results]
        assert populate_db_for_query10["emp_alice_id"] in emp_ids
        assert populate_db_for_query10["emp_charlie_id"] in emp_ids
        assert populate_db_for_query10["emp_bob_id"] not in emp_ids

    def test_get_employees_working_on_date_single(self, report_service, populate_db_for_query10):
        """Tests Part 2: Get employees working on 'other_day'."""
        # Arrange
        other_day = populate_db_for_query10["other_day"]
        # Expected: Bob

        # Act
        results = report_service.get_employees_working_on_date(other_day)

        # Assert
        assert len(results) == 1
        assert results[0][0].id == populate_db_for_query10["emp_bob_id"]

    def test_get_employees_working_on_date_empty(self, report_service, populate_db_for_query10):
        """Tests Part 2: Get employees working on an empty day."""
        # Arrange
        empty_day = populate_db_for_query10["empty_day"]

        # Act
        results = report_service.get_employees_working_on_date(empty_day)

        # Assert
        assert len(results) == 0

    def test_get_employee_rental_details_success(self, report_service, populate_db_for_query10):
        """Tests Part 1: Get all employee rental history."""
        # Arrange
        # Expected: 3 rentals total (2 by Alice, 1 by Bob)

        # Act
        results = report_service.get_employee_rental_details()

        # Assert
        assert len(results) == 3

        alice_rentals = [r for r in results if r.full_name == "Alice Q10"]
        bob_rentals = [r for r in results if r.full_name == "Bob Q10"]

        assert len(alice_rentals) == 2
        assert len(bob_rentals) == 1

        assert bob_rentals[0].model == "Atomic Skis"
        assert bob_rentals[0].equipment_type == "Skis"

        assert alice_rentals[0].model == "Atomic Skis"
        assert alice_rentals[1].model == "Burton Board"

    def test_get_employees_working_on_date_handles_none(self, report_service):
        """Tests Part 2: Handles None input gracefully."""
        # Act
        results = report_service.get_employees_working_on_date(None)
        # Assert
        assert results == []


# --- Tests requiring an EMPTY database ---
# (Moved outside the class to avoid populate_db_for_query10 fixture)

def test_get_employee_rental_details_empty(report_service, init_database):
    """Tests Part 1: Get rental history when DB is empty."""
    # Arrange (use clean init_database)

    # Act
    results = report_service.get_employee_rental_details()

    # Assert
    assert len(results) == 0