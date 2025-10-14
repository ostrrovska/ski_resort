from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.lift_service import LiftService

lift_service = LiftService()

lift_controller = Blueprint('lift', __name__)

@lift_controller.route('/', methods=['GET'])
def list_lifts():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    lifts = lift_service.get_all(sort_by=sort_by, sort_order=sort_order, filter_by=filter_by,
                                 filter_value=filter_value)

    return render_template('lifts.html', lifts=lifts)

@lift_controller.route('/view', methods=['GET'])
def view_lifts():
    lifts = lift_service.get_all()
    return render_template('guest_lifts.html', lifts=lifts)

@lift_controller.route('/browse', methods=['GET'])
def browse_lifts():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    lifts = lift_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                 filter_by=filter_by, filter_value=filter_value)

    return render_template('authorized_lifts.html', lifts=lifts)

@lift_controller.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    height = request.form['height']
    try:
        lift_service.add(name, height)
        flash('Lift added successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('lift.list_lifts'))

@lift_controller.route('/edit/<int:id>', methods=['GET'])
def edit_lift(id):
    lift = lift_service.get_by_id(id)
    if not lift:
        return redirect(url_for('lift.list_lifts'))
    return render_template('lift_edit.html', lift=lift)

@lift_controller.route('/update/<int:id>', methods=['POST'])
def update(id):
    name = request.form['name']
    height = request.form['height']

    if not name or not height:
        flash('Name and height are required.', 'warning')
        return redirect(url_for('lift.edit_lift', id=id))

    try:
        lift_service.update(id, name, height)
        flash('Lift updated successfully.', 'success')
        return redirect(url_for('lift.list_lifts'))
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('lift.edit_lift', id=id))

@lift_controller.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    lift_service.delete(id)
    return redirect(url_for('lift.list_lifts'))