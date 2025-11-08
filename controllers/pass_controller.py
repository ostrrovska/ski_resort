from flask import Blueprint, render_template, request, redirect, url_for, flash

from middlewares.authorization import roles_required
from services.pass_service import PassService

pass_service = PassService()

pass_controller = Blueprint('pass', __name__)

@pass_controller.route('/', methods=['GET'])
def list_passes():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')

    # Новий стиль (для модераторів)
    filter_cols = request.args.getlist('filter_col')
    filter_ops = request.args.getlist('filter_op')
    filter_vals = request.args.getlist('filter_val')

    passes = pass_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                  filter_cols=filter_cols, filter_ops=filter_ops, filter_vals=filter_vals)

    active_filters = list(zip(filter_cols, filter_ops, filter_vals))
    return render_template('passes.html', passes=passes,
                           active_filters = active_filters,
                           sort_by = sort_by,
                           sort_order = sort_order
                           )

@pass_controller.route('/add', methods=['POST'])
@roles_required('admin', 'moderator')
def add():
    client_id = request.form['client_id']
    pass_type_id = request.form['pass_type_id']
    purchase_date = request.form['purchase_date']
    valid_from = request.form['valid_from']
    valid_to = request.form['valid_to']
    try:
        pass_service.add(client_id, pass_type_id, purchase_date, valid_from, valid_to)
        flash('Pass added successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('pass.list_passes'))

@pass_controller.route('/edit/<int:id>', methods=['GET'])
@roles_required('admin', 'moderator')
def edit_pass(id):
    pass_ = pass_service.get_by_id(id)
    if not pass_:
        return redirect(url_for('pass.list_passes'))
    return render_template('pass_edit.html', pass_=pass_)

@pass_controller.route('/update/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
def update(id):
    client_id = request.form['client_id']
    pass_type_id = request.form['pass_type_id']
    purchase_date = request.form['purchase_date']
    valid_from = request.form['valid_from']
    valid_to = request.form['valid_to']
    remaining_lifts = request.form['remaining_lifts']
    remaining_hours = request.form['remaining_hours']

    if (not client_id or not pass_type_id or not purchase_date or not valid_from or not valid_to
            or not remaining_lifts or not remaining_hours):
        flash('All fields are required.', 'warning')
        return redirect(url_for('pass.edit_pass', id=id))
    try:
        pass_service.update(id, client_id, pass_type_id, purchase_date, valid_from, valid_to,
                            remaining_lifts, remaining_hours)
        flash('Pass updated successfully.', 'success')
        return redirect(url_for('pass.list_passes'))
    except ValueError as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('pass.edit_pass', id=id))

@pass_controller.route('/delete/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
def delete(id):
    pass_service.delete(id)
    return redirect(url_for('pass.list_passes'))