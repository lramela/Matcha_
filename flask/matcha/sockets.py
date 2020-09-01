from matcha import socket, logged_in_users, db
from matcha.utils import calculate_popularity, send_registration_email
from flask import session, request
from flask_socketio import join_room, leave_room
import secrets
from bson.objectid import ObjectId

@socket.on("connect")
def connect():
    user_name = session.get("username")
    logged_in_users[user_name] = request.sid
    print(user_name, "connected: id -", logged_in_users[user_name])

@socket.on("disconnect")
def disconnect():
    logged_in_users[session.get("username")] = ""

@socket.on("like")
def like(data):
    liker = db.get_user(
        {"username": session.get("username")}, {"username": 1, "likes": 1}
    )
    liked = db.get_user(
        {"username": data["to"]}, {"username": 1, "likes": 1, "liked": 1, "notifications": 1}
    )
    liker["likes"].append(liked["username"])
    liked["liked"].append(liker["username"])

    db.update_likes(liker["_id"], {"likes": liker["likes"]})
    db.update_likes(liked["_id"], {"liked": liked["liked"]})
    calculate_popularity(liked)
    # sid = logged_in_users.get(data["to"])
    # if sid:
    #     socket.emit("flirt", {"from": session.get("username")}, room=sid)
    liked["notifications"].append(session.get("username") + " liked you")
    db.update_likes(liked["_id"], {"notifications": liked["notifications"]})

@socket.on("view")
def view_user_profile(data):
    print("recieving the data")
    viewed_user = db.get_user({"_id": ObjectId(data["viewed"])})
    viewer = db.get_user({"_id": ObjectId(data["viewer"])}, {"username": 1})
    if (
        data["viewer"] in viewed_user["views"]
        or viewer["_id"] in viewed_user["blocked"]
    ):
        return False
    if viewed_user["username"] in logged_in_users:
        socket.emit(
            "notif_view",
            {"from": viewer["username"]},
            sid=logged_in_users[viewed_user["username"]],
        )
    if viewed_user['username'] != viewer['username']:
        viewed_user["notifications"].append(viewer["username"] + " has viewed you profile")
        viewed_user["views"].append(data["viewer"])
        db.update_likes(
            viewed_user["_id"],
            {"views": viewed_user["views"], "notifications": viewed_user["notifications"]},
        )
    print("Debug: views", data)

@socket.on("read")
def read(data):
    print("notifications read")
    user = db.get_user({"username": session.get("username")}, {"notifications": 1})
    user["notifications"] = []
    db.update_likes(user["_id"], {"notifications": user["notifications"]})

@socket.on("like-back")
def liked_back(data):

    print(f"Debug")
    like_back = db.get_user(
        {"username": session.get("username")},
        {"username": 1, "likes": 1, "matched": 1, "rooms": 1},
    )

    liked = db.get_user(
        {"username": data["to"]},
        {"username": 1, "liked": 1, "matched": 1, "rooms": 1, "notifications": 1},
    )

    room = secrets.token_hex(16)


    like_back["likes"].append(liked["username"])
    liked["liked"].append(like_back["username"])
    # add to the matched array.
    like_back["matched"].append(liked["username"])
    liked["matched"].append(like_back["username"])
    # add a unique room to this twos matched
    like_back["rooms"][liked["username"]] = room
    liked["rooms"][like_back["username"]] = room
    db.update_likes(
        like_back["_id"],
        {
            "likes": like_back["likes"],
            "matched": like_back["matched"],
            "rooms": like_back["rooms"],
        },
    )
    db.update_likes(
        liked["_id"],
        {
            "liked": liked["liked"],
            "matched": liked["matched"],
            "rooms": liked["rooms"],
        },
    )

    sid = logged_in_users.get(data["to"])
    if sid:
        socket.emit("matched", {"from": session.get("username")}, room=sid)
    liked["notifications"].append(
        session.get("username") + " has liked back. You can now chat"
    )
    db.update_likes(liked["_id"], {"notifications": liked["notifications"]})
    print(data)

@socket.on("Unlike")
def unlike(data):

    print(f"Unlike {data}")

    current_user = db.get_user(
        {"username": session.get("username")}, {"likes": 1, "matched": 1}
    )

    unlikes = db.get_user(
        {"username": data["to"]}, {"liked": 1, "matched": 1, "notifications": 1}
    )
    if data["to"] in current_user["likes"]:
        current_user["likes"].remove(data["to"])
        unlikes["liked"].remove(session.get("username"))
    if current_user["matched"] and data["to"] in current_user["matched"]:
        current_user["matched"].remove(data["to"])
        unlikes["matched"].remove(session.get("username"))

    db.update_likes(
        current_user["_id"],
        {"likes": current_user["likes"], "matched": current_user["matched"]},
    )
    db.update_likes(
        unlikes["_id"], {"liked": unlikes["liked"], "matched": unlikes["matched"]}
    )

    # sid = logged_in_users[data["to"]]
    # if sid:
    #     socket.emit("Unlike", {"from": session.get("username")}, room=sid)

    unlikes["notifications"].append(session.get("username") + " has unliked you.")
    db.update_likes(unlikes["_id"], {"notifications": unlikes["notifications"]})

def join(data):
    join_room(data)

@socket.on("send")
def send(data):
    print(f"Sending message")
    users = db.users()
    current_user = db.get_user({"username": session.get("username")}, {"_id": 1})
    notification = None

    for user in users:
        if data["room"] in user["rooms"].values() and not user[
            "username"
        ] == session.get("username"):
            notification = user
            break

    if current_user["_id"] in user["blocked"]:
        return False

    db.insert_chat(data["from"], data["room"], data["message"])
    socket.emit(
        "recieve",
        {"from": data["from"], "message": data["message"]},
        include_self=False,
        room=data["room"],
    )
    if not notification["username"] in logged_in_users:
        # send email
        notification["notifications"].append(
            session.get("username") + " has sent you a message"
        )
        db.update_likes(
            notification["_id"], {"notifications": notification["notifications"]}
        )
    else:
        notification["notifications"].append(
            session.get("username") + " has sent you a message"
        )
        db.update_likes(
            notification["_id"], {"notifications": notification["notifications"]}
        )

@socket.on("leave")
def leave(data):
    leave_room(data)