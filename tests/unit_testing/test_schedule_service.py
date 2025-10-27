import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, time
from services.schedule_service import ScheduleService
from models.schedule import Schedule
from models.employee import Employee
from models import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.attributes import InstrumentedAttribute

# Constants for patching
DB_SESSION_PATH = 'services.schedule_service.db.session'
EMP_SERVICE_PATH = 'services.schedule_service.EmployeeService.get_by_id'
SCHEDULE_QUERY_PATH = 'services.schedule_service.Schedule.query'
SCHEDULE_SERVICE_GET_BY_ID_PATH = 'services.schedule_service.ScheduleService.get_by_id'

pytestmark = pytest.mark.usefixtures("app_context")


@pytest.fixture
def schedule_service():
    """Provides a fresh instance of the ScheduleService for each test."""
    return ScheduleService()


@pytest.fixture
def mock_employee():
    """Provides a reusable mock Employee object."""
    emp = Mock(spec=Employee)
    emp.id = 1
    return emp


# Test 1: get_by_id (2 cases)
@pytest.mark.parametrize("schedule_id, mock_return, expected_id", [
    (1, Mock(id=1, employee_id=1), 1),  # Case: Found
    (999, None, None),  # Case: Not Found
])
@patch(SCHEDULE_QUERY_PATH)
def test_get_by_id(mock_schedule_query, schedule_service, schedule_id, mock_return, expected_id):
    """
    Unit test for get_by_id.
    Mocks the DB query to isolate the service.
    """
    # Arrange
    mock_schedule_query.get.return_value = mock_return

    # Act
    result = schedule_service.get_by_id(schedule_id)

    # Assert
    mock_schedule_query.get.assert_called_once_with(schedule_id)
    if expected_id is not None:
        assert result.id == expected_id
    else:
        assert result is None


# Test 2: add (2 cases)
@pytest.mark.parametrize("employee_exists, should_raise_error", [
    (True, False),  # Case: Employee found, add successfully
    (False, True),  # Case: Employee not found, raise ValueError
])
@patch(DB_SESSION_PATH)
@patch(EMP_SERVICE_PATH)
def test_add(mock_emp_service, mock_db, schedule_service, mock_employee, employee_exists, should_raise_error):
    """
    Unit test for add.
    Mocks EmployeeService and db.session.
    """
    # Arrange
    emp_id = 1
    work_date = date(2025, 10, 20)
    shift_start = time(9, 0, 0)
    shift_end = time(17, 0, 0)

    if employee_exists:
        mock_emp_service.return_value = mock_employee
    else:
        mock_emp_service.return_value = None

    # Act & Assert
    if should_raise_error:
        with pytest.raises(ValueError, match=f"Employee with ID {emp_id} is not found."):
            schedule_service.add(emp_id, work_date, shift_start, shift_end)
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    else:
        new_schedule = schedule_service.add(emp_id, work_date, shift_start, shift_end)
        mock_emp_service.assert_called_once_with(emp_id)
        mock_db.add.assert_called_once_with(new_schedule)
        mock_db.commit.assert_called_once()
        assert new_schedule.employee_id == emp_id
        assert new_schedule.work_date == work_date


# Test 3: update (3 cases)
@pytest.mark.parametrize("schedule_found, employee_found, expected_result_type", [
    (True, True, "success"),  # Case: Success
    (False, True, "schedule_none"),  # Case: Schedule to update not found
    (True, False, "employee_error"),  # Case: New employee_id not found
])
@patch(DB_SESSION_PATH)
@patch(EMP_SERVICE_PATH)
@patch(SCHEDULE_SERVICE_GET_BY_ID_PATH)
def test_update(mock_get_schedule, mock_emp_service, mock_db, schedule_service, mock_employee,
                schedule_found, employee_found, expected_result_type):
    """
    Unit test for update.
    Mocks dependent services and self.get_by_id.
    """
    # Arrange
    schedule_id = 1
    new_emp_id = 2
    new_date = date(2025, 11, 11)

    mock_schedule = Mock(spec=Schedule)
    mock_get_schedule.return_value = mock_schedule if schedule_found else None
    mock_emp_service.return_value = mock_employee if employee_found else None

    # Act & Assert
    if expected_result_type == "employee_error":
        with pytest.raises(ValueError, match=f"Employee with ID {new_emp_id} is not found."):
            schedule_service.update(schedule_id, new_emp_id, new_date, time(8), time(16))
        mock_db.commit.assert_not_called()

    elif expected_result_type == "schedule_none":
        result = schedule_service.update(schedule_id, new_emp_id, new_date, time(8), time(16))
        assert result is None
        mock_db.commit.assert_not_called()

    elif expected_result_type == "success":
        result = schedule_service.update(schedule_id, new_emp_id, new_date, time(8), time(16))

        # Check that the object was updated
        assert mock_schedule.employee_id == new_emp_id
        assert mock_schedule.work_date == new_date
        mock_db.commit.assert_called_once()
        assert result == mock_schedule


# Test 4: delete (2 cases)
@pytest.mark.parametrize("schedule_found, expected_result", [
    (True, True),  # Case: Success
    (False, False),  # Case: Not Found
])
@patch(DB_SESSION_PATH)
@patch(SCHEDULE_SERVICE_GET_BY_ID_PATH)
def test_delete(mock_get_schedule, mock_db, schedule_service, schedule_found, expected_result):
    """
    Unit test for delete.
    Mocks self.get_by_id and db.session.
    """
    # Arrange
    schedule_id = 1
    mock_schedule = Mock(spec=Schedule)
    mock_get_schedule.return_value = mock_schedule if schedule_found else None

    # Act
    result = schedule_service.delete(schedule_id)

    # Assert
    mock_get_schedule.assert_called_once_with(schedule_id)
    assert result == expected_result
    if schedule_found:
        mock_db.delete.assert_called_once_with(mock_schedule)
        mock_db.commit.assert_called_once()
    else:
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()


# Test 5: get_all sorting (5 cases)
@pytest.mark.parametrize("sort_by, sort_order, expected_field", [
    ("id", "asc", "id"),
    ("employee_id", "desc", "employee_id"),
    ("work_date", "asc", "work_date"),
    ("shift_start", "desc", "shift_start"),
    (None, "asc", None),  # Case: No sorting
])
@patch(SCHEDULE_QUERY_PATH)
def test_get_all_sorting(mock_schedule_query, schedule_service,
                         sort_by, sort_order, expected_field):
    """
    Unit test for get_all sorting logic.
    Mocks the query object and checks if order_by is called correctly.
    """
    # Arrange
    mock_order_by = MagicMock()
    mock_schedule_query.order_by.return_value = mock_order_by
    mock_order_by.all.return_value = []
    mock_schedule_query.all.return_value = []

    # Act
    schedule_service.get_all(sort_by=sort_by, sort_order=sort_order)

    # Assert
    if expected_field:
        mock_schedule_query.order_by.assert_called_once()
        call_args = mock_schedule_query.order_by.call_args[0]
        called_with_arg = call_args[0]

        if sort_order == 'desc':
            assert called_with_arg.element.key == expected_field
        else:  # asc
            assert called_with_arg.key == expected_field
        mock_order_by.all.assert_called_once()
    else:
        mock_schedule_query.order_by.assert_not_called()
        mock_schedule_query.all.assert_called_once()


# Test 6: get_all filtering (3 cases)
@pytest.mark.parametrize("filter_by, filter_value, expected_db_value", [
    ("employee_id", "123", 123),
    ("work_date", "2025-10-20", date(2025, 10, 20)),
    ("shift_start", "09:00:00", time(9, 0, 0)),
])
@patch(SCHEDULE_QUERY_PATH)
def test_get_all_filtering(mock_schedule_query, schedule_service,
                           filter_by, filter_value, expected_db_value):
    """
    Unit test for get_all filtering logic.
    Mocks the query object and inspects the filter expression.
    """
    # Arrange
    mock_filter = MagicMock()
    mock_schedule_query.filter.return_value = mock_filter
    mock_filter.all.return_value = []

    # Act
    schedule_service.get_all(filter_by=filter_by, filter_value=filter_value)

    # Assert
    mock_schedule_query.filter.assert_called_once()

    filter_expression = mock_schedule_query.filter.call_args[0][0]

    assert filter_expression.left.key == filter_by
    assert filter_expression.right.value == expected_db_value
    assert isinstance(filter_expression.right.value, type(expected_db_value))
    mock_filter.all.assert_called_once()