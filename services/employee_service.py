from models.employee import Employee, db
from models.rental import Rental
from models.schedule import Schedule
from utils.query_helper import QueryHelper


class EmployeeService:

    @staticmethod
    def get_all(sort_by=None, sort_order='asc',
                filter_cols=None, filter_ops=None, filter_vals=None,
                filter_by=None, filter_value=None):

        return QueryHelper.get_all(
            Employee,
            sort_by,
            sort_order,
            filter_cols,
            filter_ops,
            filter_vals,
            filter_by=filter_by,  # <-- Передаємо старі
            filter_value=filter_value  # <-- Передаємо старі
        )

    @staticmethod
    def get_by_id(id):
        return Employee.query.get(id)

    @staticmethod
    def add(full_name, position, salary, phone_number, email):
        new_employee = Employee(full_name, position, salary, phone_number, email)
        db.session.add(new_employee)
        db.session.commit()
        return new_employee

    @staticmethod
    def update(id, full_name, position, salary, phone_number, email):
        employee = EmployeeService.get_by_id(id)
        if employee:
            employee.full_name = full_name
            employee.position = position
            employee.salary = salary
            employee.phone_number = phone_number
            employee.email = email
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete(id):
        from services.rental_service import RentalService
        employee = EmployeeService.get_by_id(id)
        if employee:
            # --- ПОЧАТОК ЗМІН ---
            # Каскадне видалення
            Schedule.query.filter_by(employee_id=id).delete(synchronize_session=False)

            # Викликаємо сервіс RentalService для коректного видалення
            rentals_to_delete = Rental.query.filter_by(employee_id=id).all()
            for rental in rentals_to_delete:
                RentalService.delete(rental.id)
            # --- КІНЕЦЬ ЗМІН ---

            db.session.delete(employee)
            db.session.commit()
            return True
        return False