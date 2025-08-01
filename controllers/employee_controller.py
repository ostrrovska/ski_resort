from flask import Blueprint, render_template, request, redirect, url_for
from services.employee_service import EmployeeService

employee_service = EmployeeService()

employee_controller = Blueprint('employee', __name__)

@employee_controller.route('/', methods = ['GET'])
def list_employees():
    employees = employee_service.get_all()
    return render_template('employees.html', employees = employees)

@employee_controller.route('/add', methods = ['POST'])
def add():
    full_name = request.form['full_name']
    position = request.form['position']
    salary = int(request.form['salary'])
    phone_number = request.form['phone_number']
    email = request.form['email']
    employee_service.add(full_name, position, salary, phone_number, email)
    return redirect(url_for('employee.list_employees'))

@employee_controller.route('/edit/<int:id>', methods = ['GET'])
def edit_employee(id):
    employee = employee_service.get_by_id(id)
    if not employee:
        return redirect(url_for('employee.list_employees'))
    return render_template('employee_edit.html', employee = employee)

@employee_controller.route('/update/<int:id>', methods = ['POST'])
def update(id):
    full_name = request.form['full_name']
    position = request.form['position']
    salary = int(request.form['salary'])
    phone_number = request.form['phone_number']
    email = request.form['email']

    if full_name and position and salary and phone_number and email:
        employee_service.update(id, full_name, position, salary, phone_number, email)

    return redirect(url_for('employee.list_employees'))

@employee_controller.route('/delete/<int:id>', methods = ['POST'])
def delete(id):
    employee_service.delete(id)
    return redirect(url_for('employee.list_employees'))