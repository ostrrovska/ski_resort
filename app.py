from flask import Flask
from controllers.employee_controller import employee_controller
from models import db
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(employee_controller)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
