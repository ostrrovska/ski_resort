import pytest
from datetime import date, time
from models import db
from models.employee import Employee
from models.schedule import Schedule
from services.schedule_service import ScheduleService
from services.employee_service import EmployeeService


@pytest.fixture(scope='function')
def init_database(app_context):
    """
    Fixture to set up and tear down the in-memory database for each test function.
    Ensures test isolation.
    """
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def schedule_service():
    """Provides an instance of the ScheduleService."""
    return ScheduleService()


@pytest.fixture(scope='function')
def employee_service():
    """Provides an instance of the EmployeeService."""
    return EmployeeService()


@pytest.fixture(scope='function')
def test_employee(init_database, employee_service):
    """
    Fixture to create a prerequisite Employee record in the in-memory DB
    for foreign key constraints.
    """
    emp = employee_service.add(
        full_name="Test Employee",
        position="Tester",
        salary=50000,
        phone_number="123456789",
        email="test@example.com"
    )
    return emp


@pytest.fixture
def sample_schedule(schedule_service, test_employee):
    """Fixture to create a single sample schedule for reuse in tests."""
    return schedule_service.add(
        employee_id=test_employee.id,
        work_date=date(2025, 10, 21),
        shift_start=time(10, 0, 0),
        shift_end=time(18, 0, 0)
    )


# --- Test Cases ---

def test_add_schedule_successfully(schedule_service, test_employee, init_database):
    """
    Test Case 1: Add a new schedule successfully.
    Pattern: Act -> Assert (Service Response) -> Assert (DB State)
    """
    emp_id = test_employee.id
    work_date = date(2025, 10, 20)
    shift_start = time(9, 0, 0)
    shift_end = time(17, 0, 0)

    new_schedule = schedule_service.add(emp_id, work_date, shift_start, shift_end)

    assert new_schedule is not None
    assert new_schedule.id is not None
    assert new_schedule.employee_id == emp_id
    assert new_schedule.work_date == work_date

    db_schedule = db.session.get(Schedule, new_schedule.id)
    assert db_schedule is not None
    assert db_schedule.shift_start == shift_start


def test_add_schedule_employee_not_found(schedule_service, init_database):
    """
    Test Case 2: Fail to add a schedule if the employee_id (FK) does not exist.
    Pattern: Act -> Assert (Raises Error)
    """
    non_existent_emp_id = 999

    with pytest.raises(ValueError, match=f"Employee with ID {non_existent_emp_id} is not found."):
        schedule_service.add(
            employee_id=non_existent_emp_id,
            work_date=date(2025, 10, 20),
            shift_start=time(9, 0, 0),
            shift_end=time(17, 0, 0)
        )


def test_get_by_id_found(schedule_service, sample_schedule, init_database):
    """
    Test Case 3: Get a schedule by its ID (record found).
    Pattern: Act -> Assert (Service Response)
    """
    found_schedule = schedule_service.get_by_id(sample_schedule.id)

    assert found_schedule is not None
    assert found_schedule.id == sample_schedule.id
    assert found_schedule.work_date == date(2025, 10, 21)


def test_get_by_id_not_found(schedule_service, init_database):
    """
    Test Case 4: Try to get a schedule by an ID that does not exist.
    Pattern: Act -> Assert (Service Response is None)
    """
    found_schedule = schedule_service.get_by_id(999)

    assert found_schedule is None


def test_update_schedule_successfully(schedule_service, sample_schedule, init_database):
    """
    Test Case 5: Update an existing schedule successfully.
    Pattern: Act -> Assert (Service Response) -> Assert (DB State)
    """
    schedule_id = sample_schedule.id
    new_date = date(2025, 11, 22)
    new_start = time(8, 0, 0)

    updated_schedule = schedule_service.update(
        id=schedule_id,
        employee_id=sample_schedule.employee_id,
        work_date=new_date,
        shift_start=new_start,
        shift_end=sample_schedule.shift_end
    )

    # Assert (Service Response)
    assert updated_schedule is not None
    assert updated_schedule.id == schedule_id
    assert updated_schedule.work_date == new_date

    # Assert (DB State)
    db_schedule = db.session.get(Schedule, schedule_id)
    assert db_schedule.work_date == new_date
    assert db_schedule.shift_start == new_start


def test_update_schedule_not_found(schedule_service, test_employee, init_database):
    """
    Test Case 6: Fail to update a schedule that does not exist.
    Pattern: Act -> Assert (Service Response is None)
    """
    result = schedule_service.update(999, test_employee.id, date.today(), time(9), time(17))

    assert result is None


def test_update_schedule_employee_not_found(schedule_service, sample_schedule, init_database):
    """
    Test Case 7: Fail to update a schedule with an invalid employee_id (FK).
    Pattern: Act -> Assert (Raises Error)
    """
    non_existent_emp_id = 999

    with pytest.raises(ValueError, match=f"Employee with ID {non_existent_emp_id} is not found."):
        schedule_service.update(
            id=sample_schedule.id,
            employee_id=non_existent_emp_id,
            work_date=sample_schedule.work_date,
            shift_start=sample_schedule.shift_start,
            shift_end=sample_schedule.shift_end
        )


def test_delete_schedule_successfully(schedule_service, sample_schedule, init_database):
    """
    Test Case 8: Delete a schedule successfully.
    Pattern: Act -> Assert (Service Response) -> Assert (DB State)
    """
    schedule_id = sample_schedule.id

    result = schedule_service.delete(schedule_id)

    assert result is True

    db_schedule = db.session.get(Schedule, schedule_id)
    assert db_schedule is None


def test_delete_schedule_not_found(schedule_service, init_database):
    """
    Test Case 9: Fail to delete a schedule that does not exist.
    Pattern: Act -> Assert (Service Response is False)
    """
    result = schedule_service.delete(999)
    assert result is False


# --- Fixture for sorting/filtering tests ---
@pytest.fixture
def populated_schedules(schedule_service, test_employee, employee_service, init_database):
    """Fixture to create multiple employees and schedules for query testing."""
    emp2 = employee_service.add("Emp Two", "Pos 2", 20000, "222", "emp2@e.com")

    s1 = schedule_service.add(test_employee.id, date(2025, 10, 20), time(9, 0, 0), time(17))  # ID 1
    s2 = schedule_service.add(test_employee.id, date(2025, 10, 22), time(9, 0, 0), time(17))  # ID 2
    s3 = schedule_service.add(emp2.id, date(2025, 10, 21), time(8, 0, 0), time(12))  # ID 3

    return {'s1': s1, 's2': s2, 's3': s3, 'emp1_id': test_employee.id, 'emp2_id': emp2.id}


def test_get_all_sorting_by_date_desc(schedule_service, populated_schedules):
    """
    Test Case 10: Get all schedules sorted by work_date descending.
    Pattern: Act -> Assert (Correct Order)
    """
    schedules = schedule_service.get_all(sort_by='work_date', sort_order='desc')

    assert len(schedules) == 3
    ids = [s.id for s in schedules]
    # Expected order: 22nd (s2), 21st (s3), 20th (s1)
    assert ids == [populated_schedules['s2'].id, populated_schedules['s3'].id, populated_schedules['s1'].id]


def test_get_all_filtering_by_date(schedule_service, populated_schedules):
    """
    Test Case 11: Get all schedules filtered by a specific work_date.
    Pattern: Act -> Assert (Correct Items)
    """
    target_date_str = "2025-10-21"

    schedules = schedule_service.get_all(filter_by='work_date', filter_value=target_date_str)

    assert len(schedules) == 1
    assert schedules[0].id == populated_schedules['s3'].id
    assert schedules[0].work_date == date(2025, 10, 21)


def test_get_all_filtering_by_employee_id(schedule_service, populated_schedules):
    """
    Test Case 12: Get all schedules filtered by a specific employee_id.
    Pattern: Act -> Assert (Correct Items)
    """
    target_emp_id = populated_schedules['emp1_id']

    schedules = schedule_service.get_all(filter_by='employee_id', filter_value=str(target_emp_id))

    assert len(schedules) == 2
    # Check that both returned schedules belong to the target employee
    assert all(s.employee_id == target_emp_id for s in schedules)
    assert populated_schedules['s1'].id in [s.id for s in schedules]
    assert populated_schedules['s2'].id in [s.id for s in schedules]


def test_get_all_filtering_by_shift_start(schedule_service, populated_schedules):
    """
    Test Case 13: Get all schedules filtered by a specific shift_start time.
    Pattern: Act -> Assert (Correct Items)
    """
    target_time_str = "08:00:00"

    schedules = schedule_service.get_all(filter_by='shift_start', filter_value=target_time_str)

    assert len(schedules) == 1
    assert schedules[0].id == populated_schedules['s3'].id
    assert schedules[0].shift_start == time(8, 0, 0)