from models.employee import Employee

class EmployeeService:
    def __init__(self):
        self._employees = [
            Employee("Kate", 19),
            Employee("John", 20)
        ]
    def get_all(self):
        return self._employees

    def get_by_name(self, name):
        for employee in self._employees:
            if employee.name == name:
                return employee
        return None

    def add(self, name, age):
        self._employees.append(Employee(name, age))

    def update(self, name, age):
        employee = self.get_by_name(name)
        if employee:
            employee.age = age
            return True
        return False