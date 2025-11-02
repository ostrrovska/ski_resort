# controllers/reports_controller.py
from flask import Blueprint, render_template, flash
from services.report_service import ReportService
from middlewares.authorization import roles_required
from flask import Blueprint, render_template, request, flash
import datetime

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


@report_controller.route('/equipment_rental_stats', methods=['GET', 'POST'])
@roles_required('admin', 'moderator', 'authorized')
def equipment_rental_stats():
    """Запит 2: Отримати статистику оренди обладнання (найпопулярніше за тиждень, кількість за типом за день)."""

    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')
            specific_date_str = request.form.get('specific_date')

            if not start_date_str or not specific_date_str:
                flash('Please select both a start date for the week and a specific day.', 'warning')
                return render_template('report_results/equipment_stats_params.html',
                                       start_date=start_date_str,
                                       specific_date=specific_date_str)

            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            specific_date = datetime.datetime.strptime(specific_date_str, '%Y-%m-%d').date()

            end_date = start_date + datetime.timedelta(days=6)

            most_rented_weekly = report_service.get_most_rented_equipment_weekly(start_date, end_date)
            count_by_type_daily = report_service.get_equipment_count_by_type_daily(specific_date)

            return render_template('report_results/equipment_stats.html',
                                   most_rented_weekly=most_rented_weekly,
                                   count_by_type_daily=count_by_type_daily,
                                   start_date=start_date,
                                   end_date=end_date,
                                   specific_date=specific_date)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('report_results/equipment_stats_params.html',
                                   start_date=start_date_str,
                                   specific_date=specific_date_str)
        except Exception as e:
            flash(f'Error generating report: {e}', 'danger')
            return render_template('report_results/equipment_stats_params.html',
                                   start_date=start_date_str,
                                   specific_date=specific_date_str)

    else:
        today = datetime.date.today()
        return render_template('report_results/equipment_stats_params.html',
                               start_date=today.strftime('%Y-%m-%d'),
                               specific_date=today.strftime('%Y-%m-%d'))

# --- NEW ROUTE FOR QUERY 3 ---
@report_controller.route('/pass_sales_stats', methods=['GET', 'POST'])
@roles_required('admin', 'moderator', 'authorized')
def pass_sales_stats():
    """Запит 3: Визначити скільки абонементів було видано кожного дня і кожного типу за період."""

    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')

            if not start_date_str or not end_date_str:
                flash('Please select both a start and end date.', 'warning')
                return render_template('report_results/pass_sales_params.html',
                                       start_date=start_date_str,
                                       end_date=end_date_str)

            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if end_date < start_date:
                flash('End date cannot be earlier than start date.', 'warning')
                return render_template('report_results/pass_sales_params.html',
                                       start_date=start_date_str,
                                       end_date=end_date_str)

            # Викликаємо методи сервісу
            sales_by_day = report_service.get_pass_sales_by_day(start_date, end_date)
            sales_by_type = report_service.get_pass_sales_by_type(start_date, end_date)

            # Рендеримо шаблон з результатами
            return render_template('report_results/pass_sales_stats.html',
                                   sales_by_day=sales_by_day,
                                   sales_by_type=sales_by_type,
                                   start_date=start_date,
                                   end_date=end_date)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('report_results/pass_sales_params.html',
                                   start_date=start_date_str,
                                   end_date=end_date_str)
        except Exception as e:
            flash(f'Error generating report: {e}', 'danger')
            return render_template('report_results/pass_sales_params.html',
                                   start_date=start_date_str,
                                   end_date=end_date_str)

    else:
        # GET request
        today = datetime.date.today()
        return render_template('report_results/pass_sales_params.html',
                               start_date=today.strftime('%Y-%m-%d'),
                               end_date=today.strftime('%Y-%m-%d'))
# --- END NEW ROUTE ---