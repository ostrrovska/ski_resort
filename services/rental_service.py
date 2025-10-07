import datetime
from models.rental import Rental, db
from services.client_service import ClientService
from services.employee_service import EmployeeService

class RentalService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_by=None, filter_value=None):
        query = Rental.query
        sort_filter_options = {
            'id': Rental.id,
            'client_id': Rental.client_id,
            'employee_id': Rental.employee_id,
            'rental_date': Rental.rental_date,
            'start_time': Rental.start_time,
            'end_time': Rental.end_time,
            'rental_type': Rental.rental_type,
            'total_price': Rental.total_price
        }
        if sort_by in sort_filter_options:
            if sort_order == 'desc':
                query = query.order_by(sort_filter_options[sort_by].desc())
            else:
                query = query.order_by(sort_filter_options[sort_by])

        if filter_by in sort_filter_options and filter_value:
            column = sort_filter_options[filter_by]
            if isinstance(column.type, db.Integer):
                query = query.filter(column == int(filter_value))
            elif isinstance(column.type, db.Date):
                # Parse filter_value to a date object
                date_value = datetime.datetime.strptime(filter_value, "%Y-%m-%d").date()
                query = query.filter(column == date_value)
            elif isinstance(column.type, db.Time):
                # Parse filter_value to a time object
                time_value = datetime.datetime.strptime(filter_value, "%H:%M:%S").time()
                query = query.filter(column == time_value)
            else:
                query = query.filter(column.ilike(f'%{filter_value}%'))
        return query.all()

    @staticmethod
    def get_by_id(id):
        return Rental.query.get(id)

    @staticmethod
    def add(client_id, employee_id, rental_date, start_time, end_time, rental_type, total_price):
        client = ClientService.get_by_id(client_id)
        employee = EmployeeService.get_by_id(employee_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} is not found.")
        elif not employee:
            raise ValueError(f"Employee with ID {employee_id} is not found.")
        new_rental = Rental(client_id, employee_id, rental_date, start_time, end_time, rental_type, total_price)
        db.session.add(new_rental)
        db.session.commit()
        return new_rental

    @staticmethod
    def update(id, client_id, employee_id, rental_date, start_time, end_time, rental_type, total_price):
        rental = RentalService.get_by_id(id)
        if not rental:
            return None

        client = ClientService.get_by_id(client_id)
        employee = EmployeeService.get_by_id(employee_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} is not found.")
        elif not employee:
            raise ValueError(f"Employee with ID {employee_id} is not found.")

        rental.client_id = client_id
        rental.employee_id = employee_id
        rental.rental_date = rental_date
        rental.start_time = start_time
        rental.end_time = end_time
        rental.rental_type = rental_type
        rental.total_price = total_price
        db.session.commit()
        return rental

    @staticmethod
    def delete(id):
        rental = RentalService.get_by_id(id)
        if rental:
            db.session.delete(rental)
            db.session.commit()
            return True
        return False