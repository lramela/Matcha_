from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from matcha.utils import login_required, complete_user_profile
from matcha import db

chatting = Blueprint('chat', __name__)

@chatting.route('/chat')
@login_required
@complete_user_profile
def chat():
    users = db.users()
    current_user = db.get_user({'username': session.get('username')}, {'matched': 1})
    return render_template('chat/chat.html', logged_in=session.get('username'), users=users, current_user=current_user)


@chatting.route('/room/<room>')
@login_required
@complete_user_profile
def chat_room(room):
    history = db.get_chat(room)
    chats = []
    username = ""
    
    if not history:
        db.create_history(room)
    else:
        for chat in history['chats']:
            value = (list(chat.values())[0])
            key = list(chat.keys())[0]
            data = list([key, value])
            if key != session.get('username'):
                print("Pass", key)
                # username = key
            chats.append(data)
        # user1 = db.get_user({'username': session.get('username')})
        # user2 = db.get_user({'username': username})
    # print("user1: ", user1['username'])
    print("Debug: ", chats)

    return render_template('chat/room.html', logged_in=session.get('username'), history=chats, room=room)
