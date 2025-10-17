from flask import Blueprint, render_template, request, redirect, url_for

from middlewares.authorization import roles_required
from services.employee_service import EmployeeService

employee_service = EmployeeService()

employee_controller = Blueprint('employee', __name__)

@employee_controller.route('/browse', methods=['GET'])
def browse_employees():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')
    employees = employee_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                         filter_by=filter_by, filter_value=filter_value)
    return render_template('employees.html', employees=employees)


@employee_controller.route('/add', methods=['POST'])
@roles_required('admin', 'moderator')
def add():
    full_name = request.form['full_name']
    position = request.form['position']
    salary = int(request.form['salary'])
    phone_number = request.form['phone_number']
    email = request.form['email']
    employee_service.add(full_name, position, salary, phone_number, email)
    return redirect(url_for('employee.browse_employees'))


@employee_controller.route('/edit/<int:id>', methods=['GET'])
@roles_required('admin', 'moderator')
def edit_employee(id):
    employee = employee_service.get_by_id(id)
    if not employee:
        return redirect(url_for('employee.browse_employees'))
    return render_template('employee_edit.html', employee=employee)


@employee_controller.route('/update/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
def update(id):
    full_name = request.form['full_name']
    position = request.form['position']
    salary = int(request.form['salary'])
    phone_number = request.form['phone_number']
    email = request.form['email']

    if full_name and position and salary and phone_number and email:
        employee_service.update(id, full_name, position, salary, phone_number, email)

    return redirect(url_for('employee.browse_employees'))


@employee_controller.route('/delete/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
def delete(id):
    employee_service.delete(id)
    return redirect(url_for('employee.browse_employees'))
