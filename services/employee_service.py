from models.employee import Employee, db

class EmployeeService:

    @staticmethod
    def get_all(sort_by = None, sort_order = 'asc', filter_by = None, filter_value = None):
        query = Employee.query
        sort_filter_options = {
            'id': Employee.id,
            'full_name': Employee.full_name,
            'position': Employee.position,
            'salary': Employee.salary,
            'phone_number': Employee.phone_number,
            'email': Employee.email
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
            else:
                query = query.filter(column.ilike(f'%{filter_value}%'))

        return query.all()

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
        employee = EmployeeService.get_by_id(id)
        if employee:
            db.session.delete(employee)
            db.session.commit()
            return True
        return False