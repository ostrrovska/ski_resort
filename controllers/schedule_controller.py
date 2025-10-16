from flask import Blueprint, render_template, request, redirect, url_for, flash

from middlewares.authorization import roles_required
from services.schedule_service import ScheduleService

schedule_service = ScheduleService()

schedule_controller = Blueprint('schedule', __name__)

@schedule_controller.route('/', methods = ['GET'])
def list_schedules():
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')
    schedules = schedule_service.get_all(sort_by = sort_by, sort_order = sort_order,
                                         filter_by=filter_by, filter_value=filter_value)
    return render_template('schedules.html', schedules = schedules)

@schedule_controller.route('/add', methods = ['POST'])
@roles_required('admin', 'moderator')
def add():
    employee_id = request.form['employee_id']
    work_date = request.form['work_date']
    shift_start = request.form['shift_start']
    shift_end = request.form['shift_end']
    try:
        schedule_service.add(employee_id, work_date, shift_start, shift_end)
        flash('Schedule added successfully.', 'success')
    except ValueError as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('schedule.list_schedules'))

@schedule_controller.route('/edit/<int:id>', methods = ['GET'])
@roles_required('admin', 'moderator')
def edit_schedule(id):
    schedule = schedule_service.get_by_id(id)
    if not schedule:
        return redirect(url_for('schedule.list_schedules'))
    return render_template('schedule_edit.html', schedule = schedule)

@schedule_controller.route('/update/<int:id>', methods = ['POST'])
@roles_required('admin', 'moderator')
def update(id):
    employee_id = request.form['employee_id']
    work_date = request.form['work_date']
    shift_start = request.form['shift_start']
    shift_end = request.form['shift_end']

    if not employee_id or not work_date or not shift_start or not shift_end:
        flash('All fields are required.', 'warning')
        return redirect(url_for('schedule.edit_schedule', id=id))

    try:
        schedule_service.update(id, employee_id, work_date, shift_start, shift_end)
        flash('Schedule updated successfully.', 'success')
        return redirect(url_for('schedule.list_schedules'))
    except ValueError as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('schedule.edit_schedule', id=id))

@schedule_controller.route('/delete/<int:id>', methods = ['POST'])
@roles_required('admin', 'moderator')
def delete(id):
    schedule_service.delete(id)
    return redirect(url_for('schedule.list_schedules'))