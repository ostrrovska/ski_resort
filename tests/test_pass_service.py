import pytest
from unittest.mock import Mock, patch
from datetime import date
from services.pass_service import PassService
from models.passes import Pass
from models.pass_type import PassType
from models.client import Client

# mocking path
DB_SESSION_PATH = 'services.pass_service.db.session'


@pytest.fixture
def pass_service():
    #create an instance of PassService
    return PassService()


@pytest.fixture
def mock_pass_type():
    #mock PassType object
    pt = PassType(name='Daily', limit_lifts=100, limit_hours=8, price=1000)
    pt.id = 1
    return pt


@pytest.fixture
def mock_client():
    #mock Client object
    client = Mock(spec=Client)
    client.id = 1
    return client


@patch('services.pass_service.PassTypeService.get_by_id')
@patch('services.pass_service.ClientService.get_by_id')
@patch(DB_SESSION_PATH)
def test_add_pass_successfully(mock_db_session, mock_client_service_get, mock_pass_type_service_get, pass_service,
                               mock_client, mock_pass_type):

    mock_client_service_get.return_value = mock_client
    mock_pass_type_service_get.return_value = mock_pass_type

    purchase_date = date(2023, 10, 27)
    valid_from = date(2023, 11, 1)
    valid_to = date(2023, 11, 30)

    new_pass = pass_service.add(
        client_id=1,
        pass_type_id=1,
        purchase_date=purchase_date,
        valid_from=valid_from,
        valid_to=valid_to
    )

    mock_client_service_get.assert_called_once_with(1)
    mock_pass_type_service_get.assert_called_once_with(1)

    assert isinstance(new_pass, Pass)
    assert new_pass.client_id == 1
    assert new_pass.pass_type_id == 1

    assert new_pass.remaining_lifts == mock_pass_type.limit_lifts
    assert new_pass.remaining_hours == mock_pass_type.limit_hours

    mock_db_session.add.assert_called_once_with(new_pass)
    mock_db_session.commit.assert_called_once()


@patch('services.pass_service.ClientService.get_by_id')
def test_add_pass_client_not_found(mock_client_service_get, pass_service):
    #test error handling for an invalid foreign key
    mock_client_service_get.return_value = None

    with pytest.raises(ValueError, match="Client with ID 999 is not found."):
        pass_service.add(
            client_id=999,
            pass_type_id=1,
            purchase_date=date.today(),
            valid_from=date.today(),
            valid_to=date.today()
        )


@patch('services.pass_service.PassTypeService.get_by_id')
@patch('services.pass_service.ClientService.get_by_id')
def test_add_pass_type_not_found(mock_client_service_get, mock_pass_type_service_get, pass_service, mock_client):
    #test error handling for an invalid foreign key
    mock_client_service_get.return_value = mock_client
    mock_pass_type_service_get.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="Pass type with ID 999 is not found."):
        pass_service.add(
            client_id=1,
            pass_type_id=999,
            purchase_date=date.today(),
            valid_from=date.today(),
            valid_to=date.today()
        )


#parameterized tests for add_pass()
@pytest.mark.parametrize("pass_type_details", [
    {"name": "10 Lifts", "limit_lifts": 10, "limit_hours": 0},
    {"name": "5 Hours", "limit_lifts": 0, "limit_hours": 5},
    {"name": "Premium Day", "limit_lifts": 150, "limit_hours": 10},
    {"name": "Zero Limit", "limit_lifts": 0, "limit_hours": 0},
])
@patch('services.pass_service.PassTypeService.get_by_id')
@patch('services.pass_service.ClientService.get_by_id')
@patch(DB_SESSION_PATH)
def test_add_pass_with_different_pass_types(mock_db, mock_get_client, mock_get_pass_type, pass_service, mock_client,
                                            pass_type_details):

    mock_get_client.return_value = mock_client

    # creating pass type with different parameters
    param_pass_type = PassType(
        name=pass_type_details["name"],
        limit_lifts=pass_type_details["limit_lifts"],
        limit_hours=pass_type_details["limit_hours"],
        price=500
    )
    mock_get_pass_type.return_value = param_pass_type

    new_pass = pass_service.add(1, 1, date.today(), date.today(), date.today())

    assert new_pass.remaining_lifts == pass_type_details["limit_lifts"]
    assert new_pass.remaining_hours == pass_type_details["limit_hours"]


# parametrized tests for update_pass()
@pytest.mark.parametrize("invalid_client_id, invalid_pass_type_id, expected_error", [
    (999, 1, "Client with ID 999 is not found."),
    (1, 999, "Pass type with ID 999 is not found."),
])
@patch('services.pass_service.PassTypeService.get_by_id')
@patch('services.pass_service.ClientService.get_by_id')
@patch('services.pass_service.PassService.get_by_id')
def test_update_pass_with_invalid_foreign_keys(mock_get_pass, mock_get_client, mock_get_pass_type, pass_service,
                                               mock_client, mock_pass_type, invalid_client_id, invalid_pass_type_id,
                                               expected_error):

    #mock existing pass object
    mock_get_pass.return_value = Mock(spec=Pass)

    # one of values returns None, the other one returns a valid object
    if invalid_client_id != 1:
        mock_get_client.return_value = None
        mock_get_pass_type.return_value = mock_pass_type
    else:
        mock_get_client.return_value = mock_client
        mock_get_pass_type.return_value = None

    with pytest.raises(ValueError, match=expected_error):
        pass_service.update(1, invalid_client_id, invalid_pass_type_id, date.today(), date.today(), date.today(), 10, 5)


#additional tests

@patch('services.pass_service.PassService.get_by_id')
def test_delete_pass_not_found(mock_get_by_id, pass_service):
    #test if the method returns False when the pass is not found
    mock_get_by_id.return_value = None
    result = pass_service.delete(999)
    assert result is False


@patch(DB_SESSION_PATH)
@patch('services.pass_service.PassService.get_by_id')
def test_delete_pass_successfully(mock_get_by_id, mock_db_session, pass_service):
    #test if the method returns True when the pass is found and deleted successfully
    mock_pass_to_delete = Mock(spec=Pass)
    mock_get_by_id.return_value = mock_pass_to_delete

    result = pass_service.delete(1)

    assert result is True
    mock_get_by_id.assert_called_once_with(1)
    mock_db_session.delete.assert_called_once_with(mock_pass_to_delete)
    mock_db_session.commit.assert_called_once()


@patch('services.pass_service.PassService.get_by_id')
def test_update_pass_not_found(mock_get_pass, pass_service):
    #check if the method returns None when the pass is not found
    mock_get_pass.return_value = None
    result = pass_service.update(999, 1, 1, date.today(), date.today(), date.today(), 0, 0)
    assert result is None


@patch(DB_SESSION_PATH)
@patch('services.pass_service.PassTypeService.get_by_id')
@patch('services.pass_service.ClientService.get_by_id')
@patch('services.pass_service.PassService.get_by_id')
def test_update_pass_successfully(mock_get_pass, mock_get_client, mock_get_pass_type, mock_db, pass_service,
                                  mock_client, mock_pass_type):
    #test if the method returns the updated pass object when the pass is found and updated successfully
    existing_pass = Pass(1, 1, date.today(), date.today(), date.today(), 10, 5)
    mock_get_pass.return_value = existing_pass
    mock_get_client.return_value = mock_client
    mock_get_pass_type.return_value = mock_pass_type

    updated_pass = pass_service.update(1, 2, 2, date(2024, 1, 1), date(2024, 1, 2), date(2024, 2, 2), 20, 10)

    assert updated_pass.client_id == 2
    assert updated_pass.pass_type_id == 2
    assert updated_pass.remaining_lifts == 20
    assert updated_pass.remaining_hours == 10
    mock_db.commit.assert_called_once()

#other parametrized tests for sort, filter

@pytest.mark.parametrize("sort_by, sort_order, expected_sorted_field", [
    ("id", "asc", "id"),
    ("id", "desc", "id"),
    ("purchase_date", "asc", "purchase_date"),
    ("remaining_lifts", "desc", "remaining_lifts"),
    (None, "asc", None),
])
@patch('services.pass_service.Pass.query')
def test_get_all_sorting(mock_query, pass_service, sort_by, sort_order, expected_sorted_field, app_context):
    mock_order_by = mock_query.order_by.return_value
    mock_order_by.all.return_value = []

    pass_service.get_all(sort_by=sort_by, sort_order=sort_order)

    if expected_sorted_field:
        assert mock_query.order_by.called
        called_with_arg = mock_query.order_by.call_args[0][0]

        if sort_order == 'desc':
            assert called_with_arg.element.key == expected_sorted_field
        else:
            assert called_with_arg.key == expected_sorted_field
    else:
        mock_query.order_by.assert_not_called()

@pytest.mark.parametrize("filter_by, filter_value, expected_filter_type", [
    ("client_id", 123, "integer"),
    ("pass_type_id", 456, "integer"),
    ("purchase_date", "2023-10-27", "date"),
    ("remaining_lifts", 5, "integer")
])
@patch('services.pass_service.Pass.query')
def test_get_all_filtering(mock_query, pass_service, filter_by, filter_value, expected_filter_type,
                           app_context):  # <-- Додано app_context
    mock_filter = mock_query.filter.return_value
    mock_filter.all.return_value = []

    pass_service.get_all(filter_by=filter_by, filter_value=filter_value)

    assert mock_query.filter.called
    filter_expression = mock_query.filter.call_args[0][0]

    right_side_value = filter_expression.right.value

    if expected_filter_type == "date":
        assert isinstance(right_side_value, date)
        assert right_side_value == date(2023, 10, 27)
    elif expected_filter_type == "integer":
        assert isinstance(right_side_value, int)
        assert right_side_value == int(filter_value)


@pytest.mark.parametrize("lifts, hours", [
    (0, 0),
    (-1, -5),
    (99999, 99999)
])
@patch(DB_SESSION_PATH)
@patch('services.pass_service.PassTypeService.get_by_id')
@patch('services.pass_service.ClientService.get_by_id')
@patch('services.pass_service.PassService.get_by_id')
def test_update_pass_with_edge_case_values(mock_get_pass, mock_get_client, mock_get_pass_type, mock_db,
                                           pass_service, mock_client, mock_pass_type, lifts, hours):
    existing_pass = Pass(1, 1, date.today(), date.today(), date.today(), 10, 5)
    mock_get_pass.return_value = existing_pass
    mock_get_client.return_value = mock_client
    mock_get_pass_type.return_value = mock_pass_type

    updated_pass = pass_service.update(
        id=1,
        client_id=1,
        pass_type_id=1,
        purchase_date=date.today(),
        valid_from=date.today(),
        valid_to=date.today(),
        remaining_lifts=lifts,
        remaining_hours=hours
    )

    assert updated_pass.remaining_lifts == lifts
    assert updated_pass.remaining_hours == hours
    mock_db.commit.assert_called_once()
