from functools import wraps
from flask import session, flash, redirect, url_for

def roles_required(*roles):
    """
    Декоратор, який перевіряє, чи має користувач одну з необхідних ролей.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # Перевіряємо, чи користувач залогінений і чи є його роль у списку дозволених
            if 'access_right' not in session or session['access_right'] not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('client.dashboard'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper