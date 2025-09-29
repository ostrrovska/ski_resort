from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.lift_usage_service import LiftUsageService

lift_usage_service = LiftUsageService()

lift_usage_controller = Blueprint('lift_usage', __name__)

@lift_usage_controller.route('/', methods=['GET'])
def list_lift_usages():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    lift_usages = lift_usage_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                        filter_by=filter_by, filter_value=filter_value)
    return render_template('lift_usages.html', lift_usages=lift_usages)

@lift_usage_controller.route('/add', methods=['POST'])
def add():
    client_id = request.form['client_id']
    lift_id = request.form['lift_id']
    usage_date = request.form['usage_date']
    usage_time_start = request.form['usage_time_start']
    usage_time_end = request.form['usage_time_end']
    try:
        lift_usage_service.add(client_id, lift_id, usage_date, usage_time_start, usage_time_end)
        flash('Lift usage added successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('lift_usage.list_lift_usages'))

@lift_usage_controller.route('/edit/<int:id>', methods=['GET'])
def edit_lift_usage(id):
    lift_usage = lift_usage_service.get_by_id(id)
    if not lift_usage:
        return redirect(url_for('lift_usage.list_lift_usages'))
    return render_template('lift_usage_edit.html', lift_usage=lift_usage)

@lift_usage_controller.route('/update/<int:id>', methods=['POST'])
def update(id):
    client_id = request.form['client_id']
    lift_id = request.form['lift_id']
    usage_date = request.form['usage_date']
    usage_time_start = request.form['usage_time_start']
    usage_time_end = request.form['usage_time_end']

    if not client_id or not lift_id or not usage_date or not usage_time_start or not usage_time_end:
        flash('All fields are required.', 'warning')
        return redirect(url_for('lift_usage.edit_lift_usage', id=id))
    try:
        lift_usage_service.update(id, client_id, lift_id, usage_date, usage_time_start, usage_time_end)
        flash('Lift usage updated successfully.', 'success')
        return redirect(url_for('lift_usage.list_lift_usages'))
    except ValueError as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('lift_usage.edit_lift_usage', id=id))

@lift_usage_controller.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    lift_usage_service.delete(id)
    return redirect(url_for('lift_usage.list_lift_usages'))