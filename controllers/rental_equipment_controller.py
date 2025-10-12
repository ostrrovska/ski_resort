from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.rental_equipment_service import RentalEquipmentService

rental_equipment_service = RentalEquipmentService()

rental_equipment_controller = Blueprint('rental_equipment', __name__)

@rental_equipment_controller.route('/', methods=['GET'])
def list_rental_equipments():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    rental_equipments = rental_equipment_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                        filter_by=filter_by, filter_value=filter_value)

    return render_template('rental_equipments.html', rental_equipments=rental_equipments)

@rental_equipment_controller.route('/add', methods=['POST'])
def add():
    rental_id = request.form['rental_id']
    equipment_id = request.form['equipment_id']

    try:
        rental_equipment_service.add(rental_id, equipment_id)
        flash('Rental equipment added successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('rental_equipment.list_rental_equipments'))

@rental_equipment_controller.route('/edit/<int:rental_id>/<int:equipment_id>', methods=['GET'])
def edit_rental_equipment(rental_id, equipment_id):
    rental_equipment = rental_equipment_service.get_by_id(rental_id, equipment_id)
    if not rental_equipment:
        return redirect(url_for('rental_equipment.list_rental_equipments'))
    return render_template('rental_equipment_edit.html', rental_equipment = rental_equipment)

@rental_equipment_controller.route('/update/<int:old_rental_id>/<int:old_equipment_id>', methods=['POST'])
def update(old_rental_id, old_equipment_id):
    new_rental_id = request.form['rental_id']
    new_equipment_id = request.form['equipment_id']

    if not new_rental_id or not new_equipment_id:
        flash('All fields are required.', 'warning')
        return redirect(url_for('rental_equipment.edit_rental_equipment',
                                rental_id=old_rental_id, equipment_id=old_equipment_id))
    try:
        rental_equipment_service.update(old_rental_id, old_equipment_id, new_rental_id, new_equipment_id)
        flash('Rental-Equipment link updated successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('rental_equipment.list_rental_equipments'))

@rental_equipment_controller.route('/delete/<int:rental_id>/<int:equipment_id>', methods=['POST'])
def delete(rental_id, equipment_id):
    rental_equipment_service.delete(rental_id, equipment_id)
    return redirect(url_for('rental_equipment.list_rental_equipments'))