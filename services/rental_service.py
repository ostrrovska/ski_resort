import datetime

from models.pass_rental_usage import PassRentalUsage
from models.rental import Rental, db
from models.rental_equipment import RentalEquipment
from services.client_service import ClientService
from services.employee_service import EmployeeService
from utils.query_helper import QueryHelper


class RentalService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc', filter_cols=None, filter_ops=None, filter_vals=None):
        return QueryHelper.get_all(
            Rental,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals
        )

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
            # --- ПОЧАТОК ЗМІН ---
            # Каскадне видалення: спочатку видаляємо пов'язані записи
            RentalEquipment.query.filter_by(rental_id=id).delete(synchronize_session=False)
            PassRentalUsage.query.filter_by(rental_id=id).delete(synchronize_session=False)
            # --- КІНЕЦЬ ЗМІН ---

            db.session.delete(rental)
            db.session.commit()
            return True
        return False