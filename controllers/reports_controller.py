# controllers/reports_controller.py
from flask import Blueprint, render_template, flash
from services.report_service import ReportService
from middlewares.authorization import roles_required

report_controller = Blueprint('report', __name__)
report_service = ReportService()

@report_controller.route('/')
@roles_required('admin', 'moderator', 'authorized')
def index():
    return render_template('reports.html')

@report_controller.route('/clients_and_passes')
@roles_required('admin', 'moderator', 'authorized')
def clients_and_passes():
    try:
        data = report_service.get_clients_and_passes()
        return render_template('report_results/clients_passes.html', data=data)
    except Exception as e:
        flash(f'Error generating report: {e}', 'danger')
        return render_template('reports.html') 