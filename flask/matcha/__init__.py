from flask import Flask
from flask_socketio import SocketIO
from matcha.models import DB
import secrets, re, bcrypt, html
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kueghfo734yfo8g387'
app.config['SESSION_COOKIE_SAMESITE'] = "None"

logged_in_users = {}

# Set up the socket
socket = SocketIO(app, Threaded=True, cors_allowed_origins='*', SameSite=None)

db = DB()

from matcha import seed

if not db.get_user({'username': "admin"}, {'username': 1}):
    	seed.create_fakes()

filter_users = []


from matcha.views.profile import user
from matcha.views.auth import auth
from matcha.views.home import main
from matcha.views.chat import chatting
app.register_blueprint(main)
app.register_blueprint(user)
app.register_blueprint(auth)
app.register_blueprint(chatting)

from matcha import sockets
