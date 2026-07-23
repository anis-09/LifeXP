"""
routes/auth.py
--------------
Blueprint handling registration, login, and logout routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.auth_service import register_user, login_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Render registration form; handle POST to create account."""
    # Redirect logged-in users away
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    error = None
    form_data = {}

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')

        # Persist form data so we can repopulate on error
        form_data = {'full_name': full_name, 'email': email}

        success, message, user_id = register_user(full_name, email, password, confirm)

        if success:
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            error = message

    return render_template('register.html', error=error, form_data=form_data)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Render login form; handle POST to authenticate user."""
    # Redirect already-authenticated users
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    error = None
    email_value = ''

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        email_value = email

        success, message, user = login_user(email, password)

        if success:
            # Store minimal data in session
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session.permanent = True
            return redirect(url_for('dashboard.index'))
        else:
            error = message

    return render_template('login.html', error=error, email_value=email_value)


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to landing page."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))
