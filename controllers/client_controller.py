from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.client_service import ClientService

client_service = ClientService()

client_controller = Blueprint('client', __name__)

@client_controller.route('/auth', methods = ['GET'])
def auth_page():
    return render_template('auth.html')

@client_controller.route('/register', methods = ['POST'])
def register():
    full_name = request.form['full_name']
    document_id = request.form['document_id']
    date_of_birth = request.form['date_of_birth']
    phone_number = request.form['phone_number']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    client = client_service.register(full_name, document_id, date_of_birth, phone_number, email, username, password)
    if client:
        flash('Account created successfully. Please login.')
        return redirect(url_for('client.auth_page'))
    else:
        flash('Account already exists')
        return redirect(url_for('client.auth_page'))

@client_controller.route('/login', methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    client = client_service.login(username, password)
    if client:
        session['client_id'] = client.id
        return redirect(url_for('client.list_clients'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('client.auth_page'))

@client_controller.route('/logout', methods = ['POST'])
def logout():
    session.pop('client_id', None)
    return redirect(url_for('client.auth_page'))


@client_controller.route('/', methods = ['GET'])
def list_clients():
    clients = client_service.get_all()
    return render_template('clients.html', clients = clients)

@client_controller.route('/add', methods = ['POST'])
def add():
    full_name = request.form['full_name']
    document_id = request.form['document_id']
    date_of_birth = request.form['date_of_birth']
    phone_number = request.form['phone_number']
    email = request.form['email']
    client_service.add(full_name, document_id, date_of_birth, phone_number, email)
    return redirect(url_for('client.list_clients'))

@client_controller.route('/edit/<int:id>', methods = ['GET'])
def edit_client(id):
    client = client_service.get_by_id(id)
    if not client:
        return redirect(url_for('client.list_clients'))
    return render_template('client_edit.html', client = client)

@client_controller.route('/update/<int:id>', methods = ['POST'])
def update(id):
    full_name = request.form['full_name']
    document_id = request.form['document_id']
    date_of_birth = request.form['date_of_birth']
    phone_number = request.form['phone_number']
    email = request.form['email']

    if full_name and document_id and date_of_birth and phone_number and email:
        client_service.update(id, full_name, document_id, date_of_birth, phone_number, email)

    return redirect(url_for('client.list_clients'))

@client_controller.route('/delete/<int:id>', methods = ['POST'])
def delete(id):
    client_service.delete(id)
    return redirect(url_for('client.list_clients'))