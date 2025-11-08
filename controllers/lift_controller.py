from flask import Blueprint, render_template, request, redirect, url_for, flash

from middlewares.authorization import roles_required
from services.lift_service import LiftService

lift_service = LiftService()

lift_controller = Blueprint('lift', __name__)

@lift_controller.route('/', methods=['GET'])
def list_lifts():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    # Новий стиль (для модераторів)
    filter_cols = request.args.getlist('filter_col')
    filter_ops = request.args.getlist('filter_op')
    filter_vals = request.args.getlist('filter_val')

    lifts = lift_service.get_all(
        sort_by=sort_by, sort_order=sort_order,
        filter_by=filter_by, filter_value=filter_value,
        filter_cols=filter_cols, filter_ops=filter_ops, filter_vals=filter_vals
    )
    active_filters = list(zip(filter_cols, filter_ops, filter_vals))

    return render_template('lifts.html', lifts=lifts,
                           active_filters = active_filters,
                           filter_by = filter_by,
                           filter_value = filter_value,
                           sort_by = sort_by,
                           sort_order = sort_order
                           )

@lift_controller.route('/view', methods=['GET'])
def view_lifts():
    lifts = lift_service.get_all()
    return render_template('guest_lifts.html', lifts=lifts)

@lift_controller.route('/add', methods=['POST'])
@roles_required('admin', 'moderator')
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
@roles_required('admin', 'moderator')
def edit_lift(id):
    lift = lift_service.get_by_id(id)
    if not lift:
        return redirect(url_for('lift.list_lifts'))
    return render_template('lift_edit.html', lift=lift)

@lift_controller.route('/update/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
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
@roles_required('admin', 'moderator')
def delete(id):
    lift_service.delete(id)
    return redirect(url_for('lift.list_lifts'))