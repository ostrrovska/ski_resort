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