from models.employee import Employee, db

class EmployeeService:

    @staticmethod
    def get_all():
        return Employee.query.all()

    @staticmethod
    def get_by_name(name):
        return Employee.query.get(name)

    @staticmethod
    def add(name, age):
        new_employee = Employee(name, age)
        db.session.add(new_employee)
        db.session.commit()
        return new_employee

    @staticmethod
    def update(name, age):
        employee = EmployeeService.get_by_name(name)
        if employee:
            employee.age = age
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete(name):
        employee = EmployeeService.get_by_name(name)
        if employee:
            db.session.delete(employee)
            db.session.commit()
            return True
        return False