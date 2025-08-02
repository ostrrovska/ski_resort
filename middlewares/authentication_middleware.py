from flask import session, redirect, url_for, request

def require_login_middleware(app):
    @app.before_request
    def require_login():
        if request.endpoint not in ['client.auth_page', 'client.register', 'client.login', 'static']:
            if 'client_id' not in session:
                return redirect(url_for('client.auth_page'))

