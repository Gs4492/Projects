from flask import render_template, request, redirect, url_for, session, flash
from Infrastructure.Auth.repository.user import find_user_by_username, register_user, get_role_by_user_id
from . import auth_blueprint
from Infrastructure.Auth.auth.utils import login_required
import hashlib


def verify_password(input_password, stored_hash):
    hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
    return hashed_input == stored_hash

@auth_blueprint.route('/L2C')
@login_required
def dashboard():
    return render_template('pages/L2C.html', username=session['username'], role=session['role'])

@auth_blueprint.route('/users')
@login_required
def list_users():
    if session.get('role') != 'Admin':
        flash("Admins only!")
        return redirect(url_for('auth.dashboard'))

    from Auth.repository.user import get_all_users
    users = get_all_users()
    return render_template('app/user_list.html', users=users)

@auth_blueprint.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if session.get('role') != 'Admin':
        flash("Admins only!")
        return redirect(url_for('auth.dashboard'))

    from Infrastructure.Auth.repository.user import register_user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        register_user(username, password)
        flash("User created successfully.")
        return redirect(url_for('auth.list_users'))
    return render_template('Web/user_create.html')

@auth_blueprint.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if session.get('role') != 'Admin':
        flash("Admins only!")
        return redirect(url_for('auth.dashboard'))

    from Infrastructure.Auth.repository.user import get_user_by_id, update_user
    user = get_user_by_id(user_id)
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        update_user(user_id, new_username, new_password)
        flash("User updated successfully.")
        return redirect(url_for('auth.list_users'))
    return render_template('Web/user_edit.html', user=user)

@auth_blueprint.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if session.get('role') != 'Admin':
        flash("Admins only!")
        return redirect(url_for('auth.dashboard'))

    from Infrastructure.Auth.repository.user import delete_user
    delete_user(user_id)
    flash("User deleted.")
    return redirect(url_for('auth.list_users'))

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = find_user_by_username(request.form['username'])
        if user:
            # Check if user is admin
            if get_role_by_user_id(user[0]) == 'Admin':
                hashed_input = hashlib.sha256(request.form['password'].encode()).hexdigest()
                if hashed_input == user[2]:
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['role'] = 'Admin'
                    return redirect(url_for('auth.admin_panel'))  # Admin goes to admin panel
            else:
                # Regular user with plain password
                if user[2] == request.form['password']:
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['role'] = 'User'
                    return redirect(url_for('auth.dashboard'))  # Normal user
        flash("Invalid credentials")
    return render_template('login.html')  # UNCHANGED

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        register_user(request.form['username'], request.form['password'])
        flash("Registration successful. Please log in.")
        return redirect(url_for('auth.login'))
    return render_template('register.html')  # UNCHANGED

@auth_blueprint.route('/admin_panel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if session.get('role') != 'Admin':
        flash("Access denied. Admins only.")
        return redirect(url_for('auth.login'))

    from Infrastructure.Auth.repository.user import get_all_users, assign_role_to_user, register_user, update_user, delete_user

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'assign_role':
            username = request.form['username']
            role_name = request.form['role']
            success = assign_role_to_user(username, role_name)
            flash(f"Role updated for {username}" if success else "Failed to assign role")

        elif action == 'create_user':
            register_user(request.form['username'], request.form['password'])
            flash("User created")

        elif action == 'update_user':
            update_user(request.form['user_id'], request.form['username'], request.form['password'])
            flash("User updated")

        elif action == 'delete_user':
            delete_user(request.form['user_id'])
            flash("User deleted")

        return redirect(url_for('auth.admin_panel'))

    users = get_all_users()
    return render_template('admin_panel.html', username=session['username'], role=session['role'], users=users)  # UNCHANGED

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
