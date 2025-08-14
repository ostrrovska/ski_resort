from flask import Blueprint, render_template, request, redirect, url_for
from services.pass_type_service import PassTypeService

pass_type_service = PassTypeService()

pass_type_controller = Blueprint('pass_type', __name__)

@pass_type_controller.route('/', methods = ['GET'])
def list_pass_types():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')
    pass_types = pass_type_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                           filter_by=filter_by, filter_value=filter_value)
    return render_template('pass_types.html', pass_types = pass_types)

@pass_type_controller.route('/add', methods = ['POST'])
def add():
    name = request.form['name']
    limit_lifts = request.form['limit_lifts']
    limit_hours = request.form['limit_hours']
    price = request.form['price']
    pass_type_service.add(name, limit_lifts, limit_hours, price)
    return redirect(url_for('pass_type.list_pass_types'))

@pass_type_controller.route('/edit/<int:id>', methods = ['GET'])
def edit_pass_type(id):
    pass_type = pass_type_service.get_by_id(id)
    if not pass_type:
        return redirect(url_for('pass_type.list_pass_types'))
    return render_template('pass_type_edit.html', pass_type = pass_type)

@pass_type_controller.route('/update/<int:id>', methods = ['POST'])
def update(id):
    name = request.form['name']
    limit_lifts = request.form['limit_lifts']
    limit_hours = request.form['limit_hours']
    price = request.form['price']

    if name and limit_lifts and limit_hours and price:
        pass_type_service.update(id, name, limit_lifts, limit_hours, price)

    return redirect(url_for('pass_type.list_pass_types'))

@pass_type_controller.route('/delete/<int:id>', methods = ['POST'])
def delete(id):
    pass_type_service.delete(id)
    return redirect(url_for('pass_type.list_pass_types'))