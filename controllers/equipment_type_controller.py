from flask import Blueprint, render_template, request, redirect, url_for
from services.equipment_type_service import EquipmentTypeService

equipment_type_service = EquipmentTypeService()

equipment_type_controller = Blueprint('equipment_type', __name__)

@equipment_type_controller.route('/', methods = ['GET'])
def list_equipment_types():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')
    equipment_types = equipment_type_service.get_all(sort_by = sort_by, sort_order = sort_order,
                                                    filter_by=filter_by, filter_value=filter_value)
    return render_template('equipment_types.html', equipment_types = equipment_types)

@equipment_type_controller.route('/add', methods = ['POST'])
def add():
    name = request.form['name']
    description = request.form['description']
    equipment_type_service.add(name, description)
    return redirect(url_for('equipment_type.list_equipment_types'))

@equipment_type_controller.route('/edit/<int:id>', methods = ['GET'])
def edit_equipment_type(id):
    equipment_type = equipment_type_service.get_by_id(id)
    if not equipment_type:
        return redirect(url_for('equipment_type.list_equipment_types'))
    return render_template('equipment_type_edit.html', equipment_type = equipment_type)

@equipment_type_controller.route('/update/<int:id>', methods = ['POST'])
def update(id):
    name = request.form['name']
    description = request.form['description']

    if name and description:
        equipment_type_service.update(id, name, description)

    return redirect(url_for('equipment_type.list_equipment_types'))

@equipment_type_controller.route('/delete/<int:id>', methods = ['POST'])
def delete(id):
    equipment_type_service.delete(id)
    return redirect(url_for('equipment_type.list_equipment_types'))
