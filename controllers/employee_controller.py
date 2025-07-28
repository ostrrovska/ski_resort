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
    employee_service.add(request.form['name'], request.form['age'])
    return redirect(url_for('employee.list_employees'))

@employee_controller.route('/edit/<string:name>', methods = ['GET'])
def edit_employee(name):
    employee = employee_service.get_by_name(name)
    if not employee:
        return redirect(url_for('employee.list_employees'))
    return render_template('employee_edit.html', employee = employee)

@employee_controller.route('/update/<string:name>', methods = ['POST'])
def update(name):
    age = request.form['age']
    if age:
        employee_service.update(name, age)
    return redirect(url_for('employee.list_employees'))

@employee_controller.route('/delete/<string:name>', methods = ['POST'])
def delete(name):
    employee_service.delete(name)
    return redirect(url_for('employee.list_employees'))