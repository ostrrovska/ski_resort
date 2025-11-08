from flask import Blueprint, render_template, request, redirect, url_for, flash

from middlewares.authorization import roles_required
from services.equipment_service import EquipmentService

equipment_service = EquipmentService()

equipment_controller = Blueprint('equipment', __name__)


@equipment_controller.route('/list', methods=['GET'])
def list_equipment():
    #just authorized
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    #moderators, administartors
    filter_cols = request.args.getlist('filter_cols')
    filter_ops = request.args.getlist('filter_ops')
    filter_vals = request.args.getlist('filter_vals')

    #servise will figure out
    equipment = equipment_service.get_all(
        sort_by=sort_by,
        sort_order=sort_order,
        filter_by=filter_by,
        filter_value=filter_value,
        filter_cols=filter_cols,
        filter_ops=filter_ops,
        filter_vals=filter_vals,
    )

    active_filters = list(zip(filter_cols, filter_ops, filter_vals))
    return render_template('equipment.html', equipment=equipment,
                           active_filters=active_filters,
                           filter_by=filter_by,
                           filter_value=filter_value,
                           sort_by=sort_by,
                           sort_order=sort_order
                           )

@equipment_controller.route('/add', methods=['POST'])
@roles_required('admin', 'moderator')
def add():
    type_id = request.form['type_id']
    model = request.form['model']
    is_available = 'is_available' in request.form
    try:
        equipment_service.add(type_id, model, is_available)
        flash('Equipment added', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('equipment.list_equipment'))


@equipment_controller.route('/edit/<int:id>', methods=['GET'])
@roles_required('admin', 'moderator')
def edit_equipment(id):
    equipment = equipment_service.get_by_id(id)
    if not equipment:
        return redirect(url_for('equipment.list_equipment'))
    return render_template('equipment_edit.html', equipment=equipment)


@equipment_controller.route('/update/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
def update(id):
    type_id = request.form['type_id']
    model = request.form['model']
    is_available = 'is_available' in request.form

    if not type_id or not model:
        flash('Type and model are required', 'warning')
        return redirect(url_for('equipment.edit_equipment', id=id))

    try:
        equipment_service.update(id, type_id, model, is_available)
        flash('Equipment updated.', 'success')
        return redirect(url_for('equipment.list_equipment'))
    except ValueError as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('equipment.edit_equipment', id=id))


@equipment_controller.route('/delete/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
def delete(id):
    equipment_service.delete(id)
    return redirect(url_for('equipment.list_equipment'))
