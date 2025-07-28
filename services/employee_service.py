from models.employee import Employee

class EmployeeService:
    def __init__(self):
        self._employees = [
            Employee("Kate", 19),
            Employee("John", 20)
        ]
    def get_all(self):
        return self._employees

    def add(self, name, age):
        self._employees.append(Employee(name, age))