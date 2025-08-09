from flask import Blueprint, render_template, request, redirect, url_for
from services.equipment_service import EquipmentService

equipment_service = EquipmentService()

equipment_controller = Blueprint('equipment', __name__)


@equipment_controller.route('/', methods=['GET'])
def list_equipment():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    if filter_by == 'is_available' and filter_value is None and 'filter_by' in request.args:
        filter_value = 'false'

    equipment = equipment_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                          filter_by=filter_by, filter_value=filter_value)
    return render_template('equipment.html', equipment=equipment)


@equipment_controller.route('/add', methods=['POST'])
def add():
    type_id = request.form['type_id']
    model = request.form['model']
    is_available = 'is_available' in request.form
    equipment_service.add(type_id, model, is_available)
    return redirect(url_for('equipment.list_equipment'))


@equipment_controller.route('/edit/<int:id>', methods=['GET'])
def edit_equipment(id):
    equipment = equipment_service.get_by_id(id)
    if not equipment:
        return redirect(url_for('equipment.list_equipment'))
    return render_template('equipment_edit.html', equipment=equipment)


@equipment_controller.route('/update/<int:id>', methods=['POST'])
def update(id):
    type_id = request.form['type_id']
    model = request.form['model']
    is_available = 'is_available' in request.form

    if type_id and model:
        equipment_service.update(id, type_id, model, is_available)

    return redirect(url_for('equipment.list_equipment'))

@equipment_controller.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    equipment_service.delete(id)
    return redirect(url_for('equipment.list_equipment'))
