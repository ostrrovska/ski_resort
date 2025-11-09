from flask import session, redirect, url_for, request

def require_login_middleware(app):
    @app.before_request
    def require_login():
        if request.endpoint not in ['index', 'client.register', 'client.login', 'static', 'lift.view_lifts',
                                    'pass_type.view_pass_types', 'tariff.view_tariffs',
                                    'equipment.view_equipment',
                                    'client.forgot_password', 'client.reset_token']:
            if 'client_id' not in session:
                return redirect(url_for('index'))

