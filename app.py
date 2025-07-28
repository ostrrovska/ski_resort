from flask import Flask
from controllers.employee_controller import employee_controller

app = Flask(__name__)

app.register_blueprint(employee_controller)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
