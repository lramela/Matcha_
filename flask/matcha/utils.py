from flask import url_for, redirect, session, flash, request
from functools import wraps
from matcha import db, app
import os, secrets
from werkzeug.utils import secure_filename
from PIL import Image
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from geopy.geocoders import *
from geopy.distance import *


#Deprecated
def get_user_location(current_user):
    """ Get the latitude and longitude of a user

    ARGS:
    current_user : dictionary. a list containing information that pertains the user

    returns:
    Location of a user(you can also explain)
    """
    user_location = (current_user['latlon'][0], current_user['latlon'][1])
    return user_location

#Deprecated
def get_howfar(current_user, users):
    """ Get the distance between two
    """
    return (geodesic(get_user_location(current_user), get_user_location(users)).km)

# get access to a route
def login_required(f):
    @wraps(f)
    #extend the functionalioty of the function f, use as @login_required decorator.
    def wrapper(*args, **kwargs):
        if session.get('username') is None:
            flash("Please login in first", 'info')
            return redirect( url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return wrapper

# save image
def save_image(form_pic):

    random_str = secrets.token_hex(8)
    _, file_extention = os.path.splitext(secure_filename(form_pic.filename))
    image_nf =  random_str + file_extention
    image_path = os.path.join(app.root_path, 'static/profile_pics', image_nf)

    image = Image.open(form_pic.stream)
    image.thumbnail((200,200))

    image.save(image_path)
    return image_nf

def save_image_to_gallery(form_pic):
    
    random_str = secrets.token_hex(8)
    _, file_extention = os.path.splitext(secure_filename(form_pic.filename))
    image_nf =  random_str + file_extention
    image_path = os.path.join(app.root_path, 'static/gallery_pics', image_nf)

    image = Image.open(form_pic.stream)
    image.thumbnail((200,200))

    image.save(image_path)
    return image_nf

def send_registration_email(receiver, subject='email confirmation', text=None, html=None):
    """ send and Auth email for account registration

    ARGS:
    reciever: string. username of the new account the email is sent to
    subject : string. subject of the verification email "email confirmation by default"
    text    : string. the email body  

    returns: nothing.
        uses the smtplib.SMTP_SSL() as a server to send a verification email
        to a newly registered user.
    """
    user = db.get_user({'username' : receiver}, {'username' :1 , 'email': 1})
    port = 465
    password = 'C108629d'
    senders_email = "cmukwind@student.wethinkcode.co.za"
    receivers_email = user['email']
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = senders_email
    message["To"] = receivers_email

    if not text:
        text = """\
        Hello lover!!,{}
        Welcome to Matcha.
        Don't keep your soulmate waiting, click the link and confirm your registration:
        http://localhost:5000/confirm?jrr={}""".format(user['username'],user['_id'])
        
    if not html:
        html = """\
        <html>
        <body>
            <p>Hello lovera!!,{}<br>
            Welcome to Matcha.<br>
            Don't keep your soulmate waiting, click the link and confirm your registration:
            <a href="http://localhost:5000/confirm?jrr={}">Confirm Email</a>
            </p>
        </body>
        </html>
        """.format(user['username'],user['_id'])
    
    _html = MIMEText(html, "html")
    plain = MIMEText(text, "plain")
    message.attach(_html)
    message.attach(plain)

    email_body = ssl._create_unverified_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=email_body) as server:
        server.login(senders_email, password)
        server.sendmail(senders_email, receivers_email, message.as_string())


def common_interest(interest1, interest2):
    """ computation of the similar interest between user
        check if interest1 is not in the list of interest two. else return a number counting
        similar interest

    ARGS:
    interest1: list. a list containing the interest of user 1
    interest2: list containing interest of user 2

    return : int.
        if the users have similar interest, return a count, that tallys the interest
    """
    if not interest1 or not interest2:
        return 0
    common_interest_count = len(set(interest1) & set(interest2)) / float(len(set(interest1) | set(interest2))) * 100
    return common_interest_count


def calculate_popularity(user):
    """ compute the the users populariy.
        if no one liked th user or popolarity is 0
        otherwise compute the (mean of likes )* 100

        Args:
        user : dict. dictionary/object of users info.

        returns:
            updates the populariry rating in the databse
    """
    total_likes = len(user['likes'])
    total_users = db.count_users()
    if total_likes == 0:
        popularity = 0
    else:
        popularity = (total_likes / total_users) * 100

    user['fame-rating'] = int(popularity)
    db.update_user(user['_id'], user)

# needed to force the user to finish creating their bio before anything.
def complete_user_profile(f):
    @wraps(f)#extend the functionalioty of the function f, use as @complete_user_profile decorator.
    def wrapper(*args, **kwargs):
        user = db.get_user({'username': session.get('username')})
        if user is None:
            return redirect( url_for('auth.login', next=request.url))
        if user['completed'] == 0:
            flash("you must first complete your profile", 'danger')
            return redirect( url_for('profile.profile', next=request.url))
        if not user['gallery']:
            flash("you must add 4 images to your gallery", 'danger')
            return redirect( url_for('profile.profile', next=request.url))
        return f(*args, **kwargs)
    return wrapper

# filter out the user with the specific interest.
def filter_interest(users, interest):
    """ filter users in A"users" common interest A"interest

    Args: 
    users: list. An iterable containing data that pertains the user
    interest: iterable(list) . an iterable of desired interest.

    return:
        a list of users with desired interest
    """
    filter_users = [user for user in users if set(interest).issubset(set(user['interests']))]
    return filter_users

# Filter out the users with a specific location.
def filter_location(users, location):
    filter_users = [user for user in users if location in user['location'][2]]
    return filter_users

# Filter out users based on the given age
def filter_age(users, age):
    if age == 29:
        filter_users = [user for user in users if user['age'] >= 18 and user['age'] <= age]
    elif age == 39:
        filter_users = [user for user in users if user['age'] >= 30 and user['age'] <= age]
    elif age == 100:
        filter_users = [user for user in users if user['age'] >= 40 and user['age'] <= age]
    return filter_users

def filter_fame(users, fame):
    """Filter out users based on the given fame

        Args:
        users: list. An iterable containing data that pertains the user
        fame : int . a number denoting the popularity of a user.
        returns:
        a list users based on the given fame
    """
    print("Fame: ", fame)
    if fame == 10:
        filter_users = [user for user in users if user['fame-rating'] >= 0 and user['fame-rating'] < fame]
    elif fame == 20:
        filter_users = [user for user in users if user['fame-rating'] >= 10 and user['fame-rating'] < fame]
    elif fame == 30:
        filter_users = [user for user in users if user['fame-rating'] >= 20 and user['fame-rating'] < fame]
    elif fame == 40:
        filter_users = [user for user in users if user['fame-rating'] >= 30 and user['fame-rating'] < fame]
    elif fame == 50:
        filter_users = [user for user in users if user['fame-rating'] >= 40 and user['fame-rating'] < fame]
    elif fame == 60:
        filter_users = [user for user in users if user['fame-rating'] >= 50 and user['fame-rating'] < fame]
    elif fame == 70:
        filter_users = [user for user in users if user['fame-rating'] >= 60 and user['fame-rating'] < fame]
    elif fame == 80:
        filter_users = [user for user in users if user['fame-rating'] >= 70 and user['fame-rating'] < fame]
    elif fame == 90:
        filter_users = [user for user in users if user['fame-rating'] >= 80 and user['fame-rating'] < fame]
    elif fame == 100:
        filter_users = [user for user in users if user['fame-rating'] >= 90 and user['fame-rating'] < fame]
    return filter_users
