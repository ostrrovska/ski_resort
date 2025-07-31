from flask import Blueprint, render_template, request, redirect, url_for
from services.schedule_service import ScheduleService

schedule_service = ScheduleService()

schedule_controller = Blueprint('schedule', __name__)

@schedule_controller.route('/', methods = ['GET'])
def list_schedules():
    schedules = schedule_service.get_all()
    return render_template('schedules.html', schedules = schedules)

@schedule_controller.route('/add', methods = ['POST'])
def add():
    employee_id = request.form['employee_id']
    work_date = request.form['work_date']
    shift_start = request.form['shift_start']
    shift_end = request.form['shift_end']
    schedule_service.add(employee_id, work_date, shift_start, shift_end)
    return redirect(url_for('schedule.list_schedules'))

@schedule_controller.route('/edit/<int:id>', methods = ['GET'])
def edit_schedule(id):
    schedule = schedule_service.get_by_id(id)
    if not schedule:
        return redirect(url_for('schedule.list_schedules'))
    return render_template('schedule_edit.html', schedule = schedule)

@schedule_controller.route('/update/<int:id>', methods = ['POST'])
def update(id):
    employee_id = request.form['employee_id']
    work_date = request.form['work_date']
    shift_start = request.form['shift_start']
    shift_end = request.form['shift_end']

    if employee_id and work_date and shift_start and shift_end:
        schedule_service.update(id, employee_id, work_date, shift_start, shift_end)

    return redirect(url_for('schedule.list_schedules'))

@schedule_controller.route('/delete/<int:id>', methods = ['POST'])
def delete(id):
    schedule_service.delete(id)
    return redirect(url_for('schedule.list_schedules'))