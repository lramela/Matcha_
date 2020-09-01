from matcha import db, logged_in_users, filter_users
from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from bson.objectid import ObjectId
from functools import wraps, cmp_to_key
from matcha.utils import common_interest, \
filter_age, filter_interest, filter_location, login_required, \
complete_user_profile, filter_fame

main = Blueprint("main", __name__)

# Create the route for the home page
@main.route("/")
@login_required
@complete_user_profile
def home():
    user = db.get_user({"username": session.get("username")}, {"notifications": 1})
    return render_template(
        "home.html", logged_in=session.get("username"), current_user=user
    )


@main.route("/users")
@login_required
@complete_user_profile
def users():
    current_user = db.get_user({"username": session.get("username")})
    blocked = current_user["blocked"]
    opp_gen = "Male" if current_user["gender"] == "Female" else "Female"
    gen = current_user["gender"]

    if current_user["sexual_orientation"] == "heterosexual":
        users = list(
            db.users(
                {
                    "_id": {"$nin": blocked},
                    "gender": opp_gen,
                    "sexual_orientation": {"$nin": ["homosexual"]},
                }
            )
        )
    elif current_user["sexual_orientation"] == "homosexual":
        users = list(
            db.users(
                {
                    "_id": {"$nin": blocked},
                    "gender": gen,
                    "sexual_orientation": {"$nin": ["heterosexual"]},
                }
            )
        )
    else:
        users = list(
            db.users(
                {
                    "$and": [
                        {"_id": {"$nin": blocked}},
                        {
                            "$or": [
                                {"sexual_orientation": "bisexual"},
                                {
                                    "$or": [
                                        {
                                            "$and": [
                                                {"sexual_orientation": "homosexual"},
                                                {"gender": gen},
                                            ]
                                        },
                                        {
                                            "$and": [
                                                {"sexual_orientation": "heterosexual"},
                                                {"gender": opp_gen},
                                            ]
                                        },
                                    ]
                                },
                            ]
                        },
                    ]
                }
            )
        )

    global filter_users
    filter_users = [
        user
        for user in users
        if user["username"] != current_user["username"]
        and common_interest(current_user["interests"], user["interests"]) >= 0
        and user["completed"] == 1
        and user['location'][2] == current_user['location'][2]
        and user['fame-rating'] >= 50
    ]

    return render_template(
        "user/users.html",
        logged_in=session.get("username"),
        users=filter_users,
        current_user=current_user,
        search=True,
    )


@main.route("/users/search_age/search", methods=["GET", "POST"])
@login_required
@complete_user_profile
def search_age():
    global filter_users
    if request.method == "POST":
        age = request.form.get("age")

        if not age.isnumeric():
            flash("invalid input for age search", "danger")
            return redirect(url_for("main.users"))
        current_user = db.get_user({"username": session.get("username")})
        blocked = current_user["blocked"]
        users = db.users({"_id": {"$nin": blocked}, "gender": {"$ne": current_user['gender']}, "completed": 1})
        age = int((age.replace(" ", "")).split(",")[0])
        filter_users = filter_age(users, age)

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=filter_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))

@main.route("/users/search_fame/search", methods=["GET", "POST"])
@login_required
@complete_user_profile
def search_fame():
    global filter_users
    if request.method == "POST":
        print("Debug 1", request.form.get("fame"))
        fame = request.form.get("fame")

        if not fame.isnumeric():
            flash("invalid input for age search", "danger")
            return redirect(url_for("main.users"))
        current_user = db.get_user({"username": session.get("username")})
        blocked = current_user["blocked"]
        users = db.users({"_id": {"$nin": blocked}, "gender": {"$ne": current_user['gender']}, "completed": 1})
        fame = int((fame.replace(" ", "")).split(",")[0])
        filter_users = filter_fame(users, fame)

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=filter_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/interest/search", methods=["GET", "POST"])
@login_required
@complete_user_profile
def search_interest():
    global filter_users

    if request.method == "POST":
        interest = []
        if request.form.get("Traveling"):
            interest.append(request.form.get("Traveling"))
        if request.form.get("Animals"):
            interest.append(request.form.get("Animals"))
        if request.form.get("Technology"):
            interest.append(request.form.get("Technology"))
        if request.form.get("Sky-diving"):
            interest.append(request.form.get("Sky-diving"))
        if request.form.get("Movies"):
            interest.append(request.form.get("Movies"))
        if request.form.get("Music"):
            interest.append(request.form.get("Music"))
        if request.form.get("Cooking"):
            interest.append(request.form.get("Cooking"))
        if request.form.get("Sports"):
            interest.append(request.form.get("Sports"))
        if request.form.get("Gaming"):
            interest.append(request.form.get("Gaming"))

        current_user = db.get_user({"username": session.get("username")})
        blocked = current_user["blocked"]
        users = db.users({"_id": {"$nin": blocked}, "gender": {"$ne": current_user['gender']}, "completed": 1})
        filter_users = filter_interest(users, interest)

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=filter_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/location/search", methods=["GET", "POST"])
@login_required
@complete_user_profile
def search_location():
    global filter_users
    print("Debug location ", request.form.get("location"))
    if request.method == "POST":
        location = request.form.get("location")
        current_user = db.get_user({"username": session.get("username")})
        blocked = current_user["blocked"]
        users = db.users({"_id": {"$nin": blocked}, "completed": 1})
        filter_users = filter_location(users, location)

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=filter_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/username/search", methods=["GET", "POST"])
@login_required
@complete_user_profile
def search_username():
    global filter_users
    if request.method == "POST":
        username = request.form.get('username')
        print(username)
        current_user = db.get_user({'username' : session.get('username')})
        blocked = current_user["blocked"]
        filter_users = list(db.users({'_id' : { '$nin' : blocked }, 'completed' : 1, 'username': username}))

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=filter_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/sort/fame/<value>", methods=["GET", "POST"])
@login_required
@complete_user_profile
def sort_fame(value):
    global filter_users
    current_user = db.get_user({"username": session.get("username")})

    if value == "Sort_d":
        sorted_users = filter_users[:]
        for i in range(len(sorted_users)):
            for k in range(len(sorted_users)):
                if sorted_users[i]["fame-rating"] > sorted_users[k]["fame-rating"]:
                    sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
        [print(user["username"], user["fame-rating"]) for user in sorted_users]

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=sorted_users,
            current_user=current_user,
            search=True,
        )
    if value == "Sort_a":
        sorted_users = filter_users[:]
        for i in range(len(sorted_users)):
            for k in range(len(sorted_users)):
                if sorted_users[i]["fame-rating"] < sorted_users[k]["fame-rating"]:
                    sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
        [print(user["username"], user["fame-rating"]) for user in sorted_users]

        a_sorted_users =  sorted_users
        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=a_sorted_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/users/sort/age/<value>", methods=["GET", "POST"])
@login_required
@complete_user_profile
def sort_age(value):
    global filter_users
    current_user = db.get_user({"username": session.get("username")})

    if value == "Sort_d":
        sorted_users = filter_users[:]
        for i in range(len(sorted_users)):
            for k in range(len(sorted_users)):
                if sorted_users[i]["age"] > sorted_users[k]["age"]:
                    sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
        [print(user["username"], user["age"]) for user in sorted_users]
        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=sorted_users,
            current_user=current_user,
            search=True,
        )
    if value == "Sort_a":
        sorted_users = filter_users[:]
        for i in range(len(sorted_users)):
            for k in range(len(sorted_users)):
                if sorted_users[i]["age"] < sorted_users[k]["age"]:
                    sorted_users[i], sorted_users[k] = sorted_users[k], sorted_users[i]
        [print(user["username"], user["age"]) for user in sorted_users]
        
        a_sorted_users =  sorted_users
        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=a_sorted_users,
            current_user=current_user,
            search=True,
        )

        return render_template(
            "user/users.html",
            logged_in=session.get("username"),
            users=filter_users,
            current_user=current_user,
            search=True,
        )

    return redirect(url_for("main.users"))


@main.route("/user/<b_id>/block", methods=["GET", "POST"])
@login_required
@complete_user_profile
def block_user(b_id):

    current_user = db.get_user({"username": session.get("username")})
    ob_id = ObjectId(b_id)
    current_user["blocked"].append(ob_id)
    db.update_user(current_user["_id"], current_user)

    return redirect(url_for("main.users"))


@main.route("/user/<b_id>/block_for_all", methods=["GET", "POST"])
@login_required
@complete_user_profile
def block_for_all(b_id):
    users = db.users()
    ob_id = ObjectId(b_id)
    for user in users:
        if not ob_id in user["blocked"]:
            user["blocked"].append(ob_id)
            db.update_user(user["_id"], user)

    return redirect(url_for("main.blocked"))


@main.route("/blocked", methods=["GET", "POST"])
@login_required
@complete_user_profile
def blocked():
    users = list(db.users({"completed": 1}))

    return render_template(
        "blocked.html", logged_in=session.get("username"), users=users
    )

