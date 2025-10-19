from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from middlewares.authorization import roles_required
from models.key import AccessRight, Key
from services.client_service import ClientService
from services.saved_view_service import SavedViewService

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
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order')
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    clients_with_keys = client_service.get_all(sort_by=sort_by, sort_order=sort_order,
                                               filter_by=filter_by, filter_value=filter_value)

    return render_template('clients.html', clients_with_keys=clients_with_keys)

@client_controller.route('/set_moderator/<int:client_id>', methods=['POST'])
@roles_required('admin')
def set_moderator(client_id):
    success = client_service.set_access_right(client_id, AccessRight.MODERATOR)
    if success:
        flash('User promoted to Moderator successfully!', 'success')
    else:
        flash('Could not promote user.', 'error')
    return redirect(url_for('client.list_clients'))

# --- Нові маршрути для керування заявками ---

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
