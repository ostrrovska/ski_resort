from flask import Flask, render_template, session, redirect, url_for
from controllers.employee_controller import employee_controller
from controllers.schedule_controller import schedule_controller
from controllers.client_controller import client_controller
from controllers.equipment_type_controller import equipment_type_controller
from controllers.equipment_controller import equipment_controller
from controllers.tariff_controller import tariff_controller
from controllers.pass_type_controller import pass_type_controller
from controllers.pass_controller import pass_controller
from controllers.lift_controller import lift_controller
from controllers.lift_usage_controller import lift_usage_controller
from controllers.pass_lift_usage_controller import pass_lift_usage_controller
from controllers.rental_controller import rental_controller
from controllers.rental_equipment_controller import rental_equipment_controller
from middlewares.authentication_middleware import require_login_middleware
from models import db
from models.saved_view import SavedView
from config import Config
from dotenv import load_dotenv
import os
load_dotenv()


app = Flask(__name__)

app.config.from_object(Config)

app.secret_key = os.getenv('SESSION_SECRET_KEY')

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'client_id' in session:
        return redirect(url_for('client.dashboard'))
    return render_template('index.html')

require_login_middleware(app)

app.register_blueprint(employee_controller, url_prefix='/employees')
app.register_blueprint(schedule_controller, url_prefix='/schedules')
app.register_blueprint(client_controller, url_prefix='/clients')

app.register_blueprint(equipment_type_controller, url_prefix='/equipment_types')

app.register_blueprint(equipment_controller, url_prefix='/equipment')

app.register_blueprint(tariff_controller, url_prefix='/tariffs')

app.register_blueprint(pass_type_controller, url_prefix='/pass_types')

app.register_blueprint(pass_controller, url_prefix='/pass')

app.register_blueprint(lift_controller, url_prefix='/lifts')

app.register_blueprint(lift_usage_controller, url_prefix='/lift_usages')

app.register_blueprint(pass_lift_usage_controller, url_prefix='/pass_lift_usages')

app.register_blueprint(rental_controller, url_prefix='/rentals')

app.register_blueprint(rental_equipment_controller, url_prefix='/rental_equipment')

if __name__ == '__main__':
    # Quick test: print all schedules for the first employee
    with app.app_context():
        from models.employee import Employee

        first_employee = Employee.query.first()
        if first_employee:
            print(f"Employee: {first_employee.full_name}")
            for schedule in first_employee.schedules:
                print(f"  Schedule: {schedule.work_date}, {schedule.shift_start} - {schedule.shift_end}")
        else:
            print("No employees found.")
    app.run(host='0.0.0.0', port=3000, debug=True)

