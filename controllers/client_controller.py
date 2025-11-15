from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from flask_mail import Message

from middlewares.authorization import roles_required
from models.client import Client
from models.key import AccessRight, Key
from services.client_service import ClientService
from services.saved_view_service import SavedViewService
from models import db, mail

client_service = ClientService()
saved_view_service = SavedViewService()

client_controller = Blueprint('client', __name__)
@client_controller.route('/register', methods=['POST'])
def register():
    full_name = request.form['full_name']
    document_id = request.form['document_id']
    date_of_birth = request.form['date_of_birth']
    phone_number = request.form['phone_number']
    email = request.form['email']
    login = request.form['login']
    password = request.form['password']
    client = client_service.register(full_name, document_id, date_of_birth, phone_number, email, login, password)
    if client:
        flash('Your registration application has been submitted for admin approval.')
        return redirect(url_for('index'))
    else:
        flash('A user with this login already exists.')
        return redirect(url_for('index'))


@client_controller.route('/login', methods=['POST'])
def login():
    login = request.form['login']
    password = request.form['password']
    result = client_service.login(login, password)  # Отримуємо результат

    if isinstance(result, Key):  # Якщо це об'єкт Key - вхід успішний
        session['client_id'] = result.client.id
        session['access_right'] = result.access_right.value
        return redirect(url_for('client.dashboard'))
    elif result == 'pending':
        flash('Your account is awaiting admin approval.')
        return redirect(url_for('index'))
    else:  # 'invalid'
        flash('Invalid login or password')
        return redirect(url_for('index'))


@client_controller.route('/logout', methods=['POST'])
def logout():
    session.pop('client_id', None)
    session.pop('access_right', None)
    return redirect(url_for('index'))

@client_controller.route('/dashboard')
def dashboard():
    if 'client_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')


@client_controller.route('/save_view', methods=['POST'])
def save_view():
    client_id = session.get('client_id')
    if not client_id:
        return redirect(url_for('index'))

    view_name = request.form.get('view_name')
    view_url = request.form.get('view_url')

    if view_name and view_url:
        saved_view_service.add(name=view_name, url=view_url, client_id=client_id)
        flash(f'Report "{view_name}" saved successfully!')
    else:
        flash('Could not save the report. Name is required.', 'error')

    return redirect(view_url or url_for('client.dashboard'))


@client_controller.route('/saved_views')
def saved_views():
    client_id = session.get('client_id')
    if not client_id:
        return redirect(url_for('index'))

    views = saved_view_service.get_by_client_id(client_id)
    return render_template('saved_views.html', saved_views=views)


@client_controller.route('/delete_view/<int:view_id>', methods=['POST'])
def delete_view(view_id):
    client_id = session.get('client_id')
    if not client_id:
        return redirect(url_for('index'))

    if saved_view_service.delete(view_id, client_id):
        flash('Report deleted successfully!')
    else:
        flash('Error deleting report.', 'error')

    return redirect(url_for('client.saved_views'))

@client_controller.route('/')
@roles_required('admin', 'moderator')
def list_clients():
    # Отримуємо параметри сортування
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')

    # Отримуємо ТІЛЬКИ НОВІ фільтри
    filter_cols = request.args.getlist('filter_col')
    filter_ops = request.args.getlist('filter_op')
    filter_vals = request.args.getlist('filter_val')

    # Старі 'filter_by' та 'filter_value' нам більше не потрібні

    clients_with_keys = client_service.get_all(
        sort_by=sort_by,
        sort_order=sort_order,
        filter_cols=filter_cols,
        filter_ops=filter_ops,
        filter_vals=filter_vals
        # Старі параметри не передаємо
    )

    # Збираємо активні фільтри, щоб передати їх у шаблон
    active_filters = list(zip(filter_cols, filter_ops, filter_vals))

    return render_template(
        'clients.html',
        clients_with_keys=clients_with_keys,
        active_filters=active_filters,  # Тільки нові
        sort_by=sort_by,
        sort_order=sort_order
        # Старі 'filter_by' та 'filter_value' не передаємо
    )

# --- ПОЧАТОК ЗМІН ---
# Замінюємо 'set_moderator' на 'update_role'
@client_controller.route('/update_role/<int:client_id>', methods=['POST'])
@roles_required('admin')
def update_role(client_id):
    new_role_str = request.form.get('role')

    # 1. Запобігаємо зміні власної ролі
    if client_id == session.get('client_id'):
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('client.list_clients'))

    # 2. Валідація нової ролі
    try:
        new_role_enum = AccessRight(new_role_str)
    except ValueError:
        flash(f'"{new_role_str}" is not a valid role.', 'danger')
        return redirect(url_for('client.list_clients'))

    # 3. Отримуємо ключ цільового клієнта, щоб перевірити його поточну роль
    target_client = client_service.get_by_id(client_id)
    if not target_client or not target_client.key:
        flash('Client not found.', 'danger')
        return redirect(url_for('client.list_clients'))

    # 4. Запобігаємо зміні ролі іншого адміністратора
    if target_client.key.access_right == AccessRight.ADMIN:
        flash('You cannot change the role of another administrator.', 'danger')
        return redirect(url_for('client.list_clients'))

    # 5. Оновлюємо роль
    success = client_service.set_access_right(client_id, new_role_enum)
    if success:
        flash(f'User role updated to {new_role_enum.value}.', 'success')
    else:
        flash('Could not update user role.', 'error')

    return redirect(url_for('client.list_clients'))
# --- КІНЕЦЬ ЗМІН ---

@client_controller.route('/pending_registrations')
@roles_required('admin')
def pending_registrations():
    pending_list = client_service.get_pending_registrations()
    return render_template('pending_registrations.html', pending_list=pending_list)


@client_controller.route('/approve_registration/<int:key_id>', methods=['POST'])
@roles_required('admin')
def approve_registration(key_id):
    if client_service.approve_registration(key_id):
        flash('Registration approved successfully.', 'success')
    else:
        flash('Error approving registration.', 'danger')
    return redirect(url_for('client.pending_registrations'))


@client_controller.route('/reject_registration/<int:key_id>', methods=['POST'])
@roles_required('admin')
def reject_registration(key_id):
    if client_service.reject_registration(key_id):
        flash('Registration rejected and deleted.', 'success')
    else:
        flash('Error rejecting registration.', 'danger')
    return redirect(url_for('client.pending_registrations'))

# --- ------------------------------------- ---

@client_controller.route('/edit/<int:id>', methods=['GET'])
@roles_required('admin', 'moderator')
def edit_client(id):
    client = client_service.get_by_id(id)
    if not client:
        return redirect(url_for('client.list_clients'))
    return render_template('client_edit.html', client=client)


@client_controller.route('/update/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
def update(id):
    full_name = request.form['full_name']
    document_id = request.form['document_id']
    date_of_birth = request.form['date_of_birth']
    phone_number = request.form['phone_number']
    email = request.form['email']

    if full_name and document_id and date_of_birth and phone_number and email:
        client_service.update(id, full_name, document_id, date_of_birth, phone_number, email)

    return redirect(url_for('client.list_clients'))


@client_controller.route('/delete/<int:id>', methods=['POST'])
@roles_required('admin', 'moderator')
def delete(id):
    client_service.delete(id)
    return redirect(url_for('client.list_clients'))

def send_reset_email(key_obj):
    """Допоміжна функція для надсилання листа."""
    token = key_obj.get_reset_token()
    client_email = key_obj.client.email
    msg = Message(
        'Password Reset Request',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[client_email]
    )
    reset_url = url_for('client.reset_token', token=token, _external=True)

    # Використовуємо простий текстовий шаблон
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    try:
        mail.send(msg)
    except Exception as e:
        flash(f'Error sending email: {e}', 'danger')
        print(f"Email Error: {e}")  # Для дебагу в консолі


@client_controller.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if 'client_id' in session:
        return redirect(url_for('client.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        client = Client.query.filter_by(email=email).first()

        if client and client.key:
            # Надсилаємо лист, навіть якщо client.key.is_approved == False
            # Це дозволяє схваленим та не схваленим користувачам відновлювати пароль
            send_reset_email(client.key)

        # Завжди показуємо однакове повідомлення, щоб не розкривати, чи існує email в базі
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('index'))

    return render_template('forgot_password.html')


@client_controller.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if 'client_id' in session:
        return redirect(url_for('client.dashboard'))

    key_obj = Key.verify_reset_token(token)
    if key_obj is None:
        flash('That is an invalid or expired token. Please try again.', 'warning')
        return redirect(url_for('client.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)

        key_obj.set_password(password)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('index'))  # Або `client.login` якщо у вас є окрема сторінка

    return render_template('reset_password.html', token=token)
