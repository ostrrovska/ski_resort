from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.rental_service import RentalService

rental_service = RentalService()

rental_controller = Blueprint('rental', __name__)

@rental_controller.route('/', methods=['GET'])
def list_rentals():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')
    rentals = rental_service.get_all(sort_by = sort_by, sort_order = sort_order,
                                         filter_by=filter_by, filter_value=filter_value)
    return render_template('rentals.html', rentals=rentals)

@rental_controller.route('/add', methods=['POST'])
def add():
    client_id = request.form.get('client_id')
    employee_id = request.form.get('employee_id')
    rental_date = request.form.get('rental_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    rental_type = request.form.get('rental_type')
    total_price = request.form.get('total_price')
    try:
        rental_service.add(client_id, employee_id, rental_date, start_time, end_time, rental_type, total_price)
        flash('Rental Added', category='success')
    except ValueError as e:
        flash(f'Error: {e}', category='danger')

    return redirect(url_for('rental.list_rentals'))

@rental_controller.route('/edit/<int:id>', methods=['GET'])
def edit_rental(id):
    rental = rental_service.get_by_id(id)
    if not rental:
        return redirect(url_for('rental.list_rentals'))
    return render_template('rental_edit.html', rental=rental)

@rental_controller.route('/update/<int:id>', methods=['POST'])
def update(id):
    client_id = request.form.get('client_id')
    employee_id = request.form.get('employee_id')
    rental_date = request.form.get('rental_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    rental_type = request.form.get('rental_type')
    total_price = request.form.get('total_price')

    if not client_id or not employee_id or not rental_date or not start_time or not end_time or not rental_type or not total_price:
        flash('All fields are required', category='warning')
        return redirect(url_for('rental.edit_rental', id=id))

    try:
        rental_service.update(id, client_id, employee_id, rental_date,
                              start_time, end_time, rental_type, total_price)
        flash('Rental Updated', category='success')
        return redirect(url_for('rental.list_rentals'))
    except ValueError as e:
        flash(f'Error: {e}', category='danger')
        return redirect(url_for('rental.edit_rental', id=id))

@rental_controller.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    rental_service.delete(id)
    return redirect(url_for('rental.list_rentals'))


