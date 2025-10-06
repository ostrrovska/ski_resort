from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.pass_lift_usage_service import PassLiftUsageService

pass_lift_usage_service = PassLiftUsageService()

pass_lift_usage_controller = Blueprint('pass_lift_usage', __name__)

@pass_lift_usage_controller.route('/', methods=['GET'])
def list_pass_lift_usages():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    pass_lift_usages = pass_lift_usage_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                        filter_by=filter_by, filter_value=filter_value)

    return render_template('pass_lift_usages.html', pass_lift_usages=pass_lift_usages)

@pass_lift_usage_controller.route('/add', methods = ['POST'])
def add():
    pass_id = request.form['pass_id']
    lift_usage_id = request.form['lift_usage_id']
    try:
        pass_lift_usage_service.add(pass_id, lift_usage_id)
        flash('Pass lift usage added successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('pass_lift_usage.list_pass_lift_usages'))

@pass_lift_usage_controller.route('/edit/<int:pass_id>/<int:lift_usage_id>', methods=['GET'])
def edit_pass_lift_usage(pass_id, lift_usage_id):
    pass_lift_usage = pass_lift_usage_service.get_by_id(pass_id, lift_usage_id)
    if not pass_lift_usage:
        return redirect(url_for('pass_lift_usage.list_pass_lift_usages'))
    return render_template('pass_lift_usage_edit.html', pass_lift_usage = pass_lift_usage)

@pass_lift_usage_controller.route('/update/<int:old_pass_id>/<int:old_lift_usage_id>', methods=['POST'])
def update(old_pass_id, old_lift_usage_id):
    new_pass_id = request.form['pass_id']
    new_lift_usage_id = request.form['lift_usage_id']

    if not new_pass_id or not new_lift_usage_id:
        flash('All fields are required.', 'warning')
        return redirect(url_for('pass_lift_usage.edit_pass_lift_usage',
                                pass_id=old_pass_id, lift_usage_id=old_lift_usage_id))
    try:
        pass_lift_usage_service.update(old_pass_id, old_lift_usage_id, new_pass_id, new_lift_usage_id)
        flash('Pass-LiftUsage link updated successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('pass_lift_usage.list_pass_lift_usages'))

@pass_lift_usage_controller.route('/delete/<int:pass_id>/<int:lift_usage_id>', methods=['POST'])
def delete(pass_id, lift_usage_id):
    pass_lift_usage_service.delete(pass_id, lift_usage_id)
    return redirect(url_for('pass_lift_usage.list_pass_lift_usages'))