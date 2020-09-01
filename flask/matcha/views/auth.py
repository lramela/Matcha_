from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from matcha import db, logged_in_users
from bson import ObjectId
from functools import wraps
import secrets, re, bcrypt, html
from matcha.utils import calculate_popularity, send_registration_email
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # blocked = db.get_user(db.get_user({'_id': ObjectId(b'admin')}, {'blocked': 1}))["blocked"]
    errors = []
    user_info = {
        'username': '',
        'firstname': '',
        'lastname': '',
        'email': '',
        'password': '',
        'gender': '',
        'sexual_orientation': 'bisexual',
        'bio': '',
        'interests': [],
        'likes': [],
        'liked': [],
        'matched': [],
        'blocked': [],
        'views': [],
        'rooms': {},
        'notifications': [],
        'fame-rating': 0,
        'location': [],
        'latlon': '',
        'age': 18,
        'image_name': 'default.png',
        'gallery': [],
        'token': secrets.token_hex(16),
        'completed': 0,
        'email_confirmed': 0,
        'last-seen': datetime.utcnow()

    }

    if request.method == 'POST':
        user_info['username'] = html.escape(request.form.get('username'))
        user_info['firstname'] = html.escape(request.form.get("firstname"))
        user_info['lastname'] = html.escape(request.form.get('lastname'))
        user_info['email'] = html.escape(request.form.get('email'))
        user_info['password'] = html.escape(request.form.get('password'))
        passwd_confirm = html.escape(request.form.get('password_confirm'))

        if not user_info['username']:
            errors.append('The username cannot be empty')
        if not re.match('^[A-Za-z][A-Za-z0-9]{2,49}$', user_info['username']):
            errors.append(
                'The username must be an alpha numeric value beginning with a letter, 3 - 50 characters long.')
        if db.get_user({'username': user_info['username']}):
            errors.append('The username is already taken')
        if db.get_user({'email': user_info['email']}):
            errors.append('The email is already taken!')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,100}$', user_info['email']):
            errors.append('invalid email format')
        if not re.match(r'^.*(?=.{8,10})(?=.*[a-zA-Z])(?=.*?[A-Z])(?=.*\d)[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$', user_info['password']):
            print(f"Debug password: {user_info['password']}")
            errors.append('The password must have an uppercase, lowercase and a digit, 5 - 25 characters long.')
        if passwd_confirm != user_info['password']:
            errors.append('The two passwords do not match')
        if not re.match('^[A-Z][a-zA-Z-]{1,24}$', user_info['firstname']):
            errors.append('A name must start with a capital letter, and a have no more than 25 characters')
        try:
            user_info['age'] = int(request.form.get('age'))
            if user_info['age'] < 18 or user_info['age'] > 100:
                errors.append("You need to be between 18 and 100 to use this site")
        except ValueError:
            errors.append("Age needs to be a number")
        if not re.match('^[A-Z][ a-zA-Z-]{1,24}$', user_info['lastname']):
            errors.append('The lastname must start with a capital letter, and have 2-24 charaters')

        if not errors:
            salt = bcrypt.gensalt()
            user_info['password'] = bcrypt.hashpw(user_info['password'].encode('utf-8'), salt)
            db.register_user(user_info)
            send_registration_email(user_info['username'])
            flash("Please check your email for confirmation", 'success')
            return redirect(url_for('auth.login'))

        for error in errors:
            flash(error, 'danger')

    return render_template('auth/register.html', user_info=user_info)


@auth.route('/confirm', methods=['GET', 'POST'])
def confirm():
    errors = []
    if request.method == 'GET':
        user_id = ObjectId(request.args.get('jrr'))

        user = db.get_user({'_id': user_id})

        if user:
            db.update_likes(user_id, {'email_confirmed': 1})
            flash('Email confirmed', 'success')
            return redirect(url_for('auth.login'))
        else:
            errors.append("Incorrect username or password")
            for error in errors:
                flash(error, 'danger')

    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    errors = []
    user_info = {
        'username': '',
        'password': ''
    }

    if request.method == 'POST':
        user_info['username'] = html.escape(request.form.get('username'))
        user_info['password'] = html.escape(request.form.get('password'))
        user = db.get_user({'username': user_info['username']})

        if not user:
            errors.append("Incorrect username or password")
        elif not user['email_confirmed']:
            errors.append('Please check your email for confirmation')
        elif not bcrypt.checkpw(user_info['password'].encode('utf-8'), user['password']):
            errors.append('Incorrect username or password')

        if not errors:
            session['username'] = user_info['username']
            flash('Successful login', 'success')
            if not user_info['username'] in logged_in_users:
                logged_in_users[user_info['username']] = ''
            calculate_popularity(user)
            return redirect(url_for('main.users'))
        for error in errors:
            flash(error, 'danger')

    return render_template('auth/login.html', user_info=user_info)


@auth.route('/logout')
def logout():
    user = db.get_user({'username': session.get('username')}, {'last-seen': 1})

    user['last-seen'] = datetime.utcnow()
    # db.update_likes(user['_id'], {'last-seen': user['last-seen']})
    db.update_user(user['_id'], {'last-seen': user['last-seen']})

    logged_in_users.pop(session.pop("username"), None)

    # session.pop('username')
    return redirect(url_for('main.home'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    errors = []
    user_info = {
        'username': ''
    }
    if request.method == 'POST':
        username = request.form.get('username')
        user = db.get_user({'username': username})

        if not username:
            errors.append('The username cannot be empty')
        if not re.match('^[A-Za-z][A-Za-z0-9]{2,49}$', username):
            errors.append('Invalid username')
        if not user:
            errors.append('No such user found, please register an account, peasant')

        if not errors:
            subject = 'Forgot Password'
            text = """\
                    Hi,{}
                    Welcome to Matcha.
                    Copy the URL below to reset your password:
                    http://localhost:5000/reset_password?jrr={}""".format(user['username'], user['_id'])
            html = """\
                    <html>
                    <body>
                        <p>Hi,{}<br>
                        Welcome to Matcha.<br>
                        Click the link below to reset your password:
                        <a href="http://localhost:5000/reset_password?jrr={}">Reset Password</a>
                        </p>
                    </body>
                    </html>
                    """.format(user['username'], user['_id'])
            send_registration_email(username, subject, text, html)
            flash('Please check your email to reset your password', 'success')
        for error in errors:
            flash(error, 'danger')

    return render_template('auth/forgot_password.html', user_info=user_info)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    errors = []

    if request.method == 'GET':
        user_id = ObjectId(request.args.get('jrr'))

    if request.method == 'POST':
        user_id = ObjectId(request.args.get('jrr'))
        user = db.get_user({'_id': user_id})
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')

        if not re.match('[A-Za-z0-9]', password):
            errors.append('The password must have an uppercase, lowercase and a digit')
        if password_repeat != password:
            errors.append('The two passwords do not match')

        if not errors:
            salt = bcrypt.gensalt()
            user['password'] = bcrypt.hashpw(password.encode('utf-8'), salt)
            db.update_user(user['_id'], user)
            return redirect(url_for('auth.login'))

        for error in errors:
            flash(error, 'danger')

    return render_template('auth/reset_password.html')
