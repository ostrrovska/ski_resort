from flask import Flask
from controllers.employee_controller import employee_controller
from controllers.schedule_controller import schedule_controller
from controllers.client_controller import client_controller
from middlewares.authentication_middleware import require_login_middleware
from models import db
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

require_login_middleware(app)

app.register_blueprint(employee_controller)
app.register_blueprint(schedule_controller, url_prefix='/schedules')
app.register_blueprint(client_controller, url_prefix='/clients')

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

