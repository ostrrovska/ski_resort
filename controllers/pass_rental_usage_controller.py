from flask import Blueprint, render_template, request, redirect, url_for, flash
from middlewares.authorization import roles_required
from services.pass_rental_usage_service import PassRentalUsageService

pass_rental_usage_service = PassRentalUsageService()

pass_rental_usage_controller = Blueprint('pass_rental_usage', __name__)


@pass_rental_usage_controller.route('/', methods=['GET'])
@roles_required('admin', 'moderator')
def list_pass_rental_usages():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_cols = request.args.getlist('filter_col')
    filter_ops = request.args.getlist('filter_op')
    filter_vals = request.args.getlist('filter_val')

    usages = pass_rental_usage_service.get_all(
        sort_by=sort_by, sort_order=sort_order,
        filter_cols=filter_cols, filter_ops=filter_ops, filter_vals=filter_vals
    )
    active_filters = list(zip(filter_cols, filter_ops, filter_vals))

    return render_template('pass_rental_usages.html',
                           pass_rental_usages=usages,
                           active_filters=active_filters,
                           sort_by=sort_by,
                           sort_order=sort_order)


@pass_rental_usage_controller.route('/add', methods=['POST'])
@roles_required('admin', 'moderator')
def add():
    pass_id = request.form['pass_id']
    rental_id = request.form['rental_id']
    try:
        pass_rental_usage_service.add(pass_id, rental_id)
        flash('Pass rental usage linked successfully. Hours deducted.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('pass_rental_usage.list_pass_rental_usages'))


@pass_rental_usage_controller.route('/edit/<int:pass_id>/<int:rental_id>', methods=['GET'])
@roles_required('admin', 'moderator')
def edit_pass_rental_usage(pass_id, rental_id):
    usage = pass_rental_usage_service.get_by_id(pass_id, rental_id)
    if not usage:
        return redirect(url_for('pass_rental_usage.list_pass_rental_usages'))
    return render_template('pass_rental_usage_edit.html', pass_rental_usage=usage)


@pass_rental_usage_controller.route('/update/<int:old_pass_id>/<int:old_rental_id>', methods=['POST'])
@roles_required('admin', 'moderator')
def update(old_pass_id, old_rental_id):
    new_pass_id = request.form['pass_id']
    new_rental_id = request.form['rental_id']

    if not new_pass_id or not new_rental_id:
        flash('All fields are required.', 'warning')
        return redirect(url_for('pass_rental_usage.edit_pass_rental_usage',
                                pass_id=old_pass_id, rental_id=old_rental_id))
    try:
        pass_rental_usage_service.update(old_pass_id, old_rental_id, new_pass_id, new_rental_id)
        flash('Pass-Rental link updated successfully. Hours recalculated.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('pass_rental_usage.list_pass_rental_usages'))


@pass_rental_usage_controller.route('/delete/<int:pass_id>/<int:rental_id>', methods=['POST'])
@roles_required('admin', 'moderator')
def delete(pass_id, rental_id):
    try:
        pass_rental_usage_service.delete(pass_id, rental_id)
        flash('Link deleted successfully. Hours refunded to pass.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('pass_rental_usage.list_pass_rental_usages'))