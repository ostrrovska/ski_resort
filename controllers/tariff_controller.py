from calendar import weekday

from flask import Blueprint, render_template, request, redirect, url_for, flash

from middlewares.authorization import roles_required
from services.tariff_service import TariffService

tariff_service = TariffService()

tariff_controller = Blueprint('tariff', __name__)

@tariff_controller.route('/', methods = ['GET'])
def list_tariffs():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')
    tariffs = tariff_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                    filter_by=filter_by, filter_value=filter_value)
    return render_template('tariffs.html', tariffs = tariffs)

@tariff_controller.route('/view', methods=['GET'])
def view_tariffs():
    tariffs = tariff_service.get_all()
    return render_template('guest_tariffs.html', tariffs=tariffs)

@tariff_controller.route('/add', methods = ['POST'])
@roles_required('admin', 'moderator')
def add():
    equipment_type_id = request.form['equipment_type_id']
    price_per_hour = request.form['price_per_hour']
    price_per_day = request.form['price_per_day']
    weekday_discount = request.form['weekday_discount']
    try:
        tariff_service.add(equipment_type_id, price_per_hour, price_per_day, weekday_discount)
        flash('Tariff added successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('tariff.list_tariffs'))

@tariff_controller.route('/edit/<int:id>', methods = ['GET'])
@roles_required('admin', 'moderator')
def edit_tariff(id):
    tariff = tariff_service.get_by_id(id)
    if not tariff:
        return redirect(url_for('tariff.list_tariffs'))
    return render_template('tariff_edit.html', tariff = tariff)

@tariff_controller.route('/update/<int:id>', methods = ['POST'])
@roles_required('admin', 'moderator')
def update(id):
    equipment_type_id = request.form['equipment_type_id']
    price_per_hour = request.form['price_per_hour']
    price_per_day = request.form['price_per_day']
    weekday_discount = request.form['weekday_discount']

    if not equipment_type_id or not price_per_hour or not price_per_day or not weekday_discount:
        flash('All fields are required.', 'warning')
        return redirect(url_for('tariff.edit_tariff', id=id))

    try:
        tariff_service.update(id, equipment_type_id, price_per_hour, price_per_day, weekday_discount)
        flash('Tariff updated successfully.', 'success')
        return redirect(url_for('tariff.list_tariffs'))
    except ValueError as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('tariff.edit_tariff', id=id))

@tariff_controller.route('/delete/<int:id>', methods = ['POST'])
@roles_required('admin', 'moderator')
def delete(id):
    tariff_service.delete(id)
    return redirect(url_for('tariff.list_tariffs'))