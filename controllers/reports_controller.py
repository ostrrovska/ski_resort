# controllers/reports_controller.py
from flask import Blueprint, render_template, flash, redirect, url_for
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


@report_controller.route('/most_used_lifts', methods=['GET', 'POST'])
@roles_required('admin', 'moderator', 'authorized')
def most_used_lifts():
    """Запит 4: Визначити найбільш використовувані підйомники за період."""

    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')

            if not start_date_str or not end_date_str:
                flash('Please select both a start and end date.', 'warning')
                return render_template('report_results/most_used_lifts_params.html',
                                       start_date=start_date_str,
                                       end_date=end_date_str)

            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if end_date < start_date:
                flash('End date cannot be earlier than start date.', 'warning')
                return render_template('report_results/most_used_lifts_params.html',
                                       start_date=start_date_str,
                                       end_date=end_date_str)

            # Викликаємо метод сервісу
            report_data = report_service.get_most_used_lifts_by_period(start_date, end_date)

            # Рендеримо шаблон з результатами
            return render_template('report_results/most_used_lifts_stats.html',
                                   data=report_data,
                                   start_date=start_date,
                                   end_date=end_date)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('report_results/most_used_lifts_params.html',
                                   start_date=start_date_str,
                                   end_date=end_date_str)
        except Exception as e:
            flash(f'Error generating report: {e}', 'danger')
            return render_template('report_results/most_used_lifts_params.html',
                                   start_date=start_date_str,
                                   end_date=end_date_str)

    else:
        # GET request
        today = datetime.date.today()
        return render_template('report_results/most_used_lifts_params.html',
                               start_date=today.strftime('%Y-%m-%d'),
                               end_date=today.strftime('%Y-%m-%d'))

@report_controller.route('/rental_revenue_stats', methods=['GET', 'POST'])
@roles_required('admin', 'moderator', 'authorized')
def rental_revenue_stats():
    """Запит 5: Обчислити загальну суму за прокат спорядження за місяцями; за кварталами."""

    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')

            if not start_date_str or not end_date_str:
                flash('Please select both a start and end date.', 'warning')
                return render_template('report_results/rental_revenue_params.html',
                                       start_date=start_date_str,
                                       end_date=end_date_str)

            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if end_date < start_date:
                flash('End date cannot be earlier than start date.', 'warning')
                return render_template('report_results/rental_revenue_params.html',
                                       start_date=start_date_str,
                                       end_date=end_date_str)

            # Викликаємо нові методи сервісу
            revenue_by_month = report_service.get_rental_revenue_by_month(start_date, end_date)
            revenue_by_quarter = report_service.get_rental_revenue_by_quarter(start_date, end_date)

            # Рендеримо шаблон з результатами
            return render_template('report_results/rental_revenue_stats.html',
                                   revenue_by_month=revenue_by_month,
                                   revenue_by_quarter=revenue_by_quarter,
                                   start_date=start_date,
                                   end_date=end_date)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('report_results/rental_revenue_params.html',
                                   start_date=start_date_str,
                                   end_date=end_date_str)
        except Exception as e:
            flash(f'Error generating report: {e}', 'danger')
            return render_template('report_results/rental_revenue_params.html',
                                   start_date=start_date_str,
                                   end_date=end_date_str)

    else:
        # GET request
        today = datetime.date.today()
        return render_template('report_results/rental_revenue_params.html',
                               start_date=today.strftime('%Y-%m-%d'),
                               end_date=today.strftime('%Y-%m-%d'))

@report_controller.route('/client_pass_stats', methods=['GET', 'POST'])
@roles_required('admin', 'moderator', 'authorized')
def client_pass_stats():
    """Запит 6: Отримати інформацію про клієнтів, які вичерпали абонементи,
                та тих, хто виконав більше 15 підйомів за день."""

    if request.method == 'POST':
        try:
            specific_date_str = request.form.get('specific_date')

            if not specific_date_str:
                flash('Please select a specific day.', 'warning')
                return render_template('report_results/client_pass_stats_params.html',
                                       specific_date=specific_date_str)

            specific_date = datetime.datetime.strptime(specific_date_str, '%Y-%m-%d').date()

            # Викликаємо методи сервісу
            exhausted_passes_clients = report_service.get_clients_with_exhausted_passes()
            over_15_lifts_clients = report_service.get_clients_with_over_15_lifts_daily(specific_date)

            # Рендеримо шаблон з результатами
            return render_template('report_results/client_pass_stats.html',
                                   exhausted_passes_clients=exhausted_passes_clients,
                                   over_15_lifts_clients=over_15_lifts_clients,
                                   specific_date=specific_date)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('report_results/client_pass_stats_params.html',
                                   specific_date=specific_date_str)
        except Exception as e:
            flash(f'Error generating report: {e}', 'danger')
            return render_template('report_results/client_pass_stats_params.html',
                                   specific_date=specific_date_str)

    else:
        # GET request
        today = datetime.date.today()
        return render_template('report_results/client_pass_stats_params.html',
                               specific_date=today.strftime('%Y-%m-%d'))

# ... (в кінці файлу controllers/reports_controller.py)

@report_controller.route('/february_unlimited_clients', methods=['GET', 'POST'])
@roles_required('admin', 'moderator', 'authorized')
def february_unlimited_clients():
    """Запит 7: Отримати інформацію про клієнтів, які придбали безлімітний абонемент у лютому."""

    PASS_NAME = "Unlimited"
    MONTH = 2  # Лютий

    if request.method == 'POST':
        try:
            year_str = request.form.get('year')
            if not year_str:
                flash('Please specify a year.', 'warning')
                return render_template('report_results/february_unlimited_clients_params.html',
                                       year=year_str)

            year = int(year_str)

            # Викликаємо метод сервісу
            clients = report_service.get_clients_bought_pass_by_month(PASS_NAME, year, MONTH)

            # Рендеримо шаблон з результатами
            return render_template('report_results/february_unlimited_clients_stats.html',
                                   clients=clients,
                                   year=year,
                                   month=MONTH,
                                   pass_name=PASS_NAME)
        except ValueError:
            flash('Invalid year format. Please enter a number.', 'danger')
            return render_template('report_results/february_unlimited_clients_params.html',
                                   year=year_str)
        except Exception as e:
            flash(f'Error generating report: {e}', 'danger')
            return render_template('report_results/february_unlimited_clients_params.html',
                                   year=year_str)

    else:
        # GET request
        default_year = datetime.date.today().year
        return render_template('report_results/february_unlimited_clients_params.html',
                               year=default_year)


# ... (в кінці файлу, після february_unlimited_clients)

@report_controller.route('/equipment_tariffs_report')
@roles_required('admin', 'moderator', 'authorized')
def equipment_tariffs_report():
    """Запит 8: Отримати інформацію про тарифи на кожен вид обладнання (вихідні/робочі дні)."""
    try:
        # Цей звіт не потребує параметрів, він просто обчислює на основі існуючих даних
        tariff_data = report_service.get_equipment_tariffs_with_weekday_discount()

        return render_template('report_results/equipment_tariffs_stats.html',
                               tariff_data=tariff_data)
    except Exception as e:
        flash(f'Error generating report: {e}', 'danger')
        return redirect(url_for('report.index'))