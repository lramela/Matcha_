from flask import Blueprint, render_template, session, redirect, flash, request, url_for
from matcha import db, logged_in_users
from bson import ObjectId
from functools import wraps
import secrets, re, bcrypt, html
#from matcha.utils import calculate_fame
from faker import Faker
import random
from datetime import datetime
import time
import sys
from tqdm import tqdm

def create_fakes():
    n = 500
    print("Be Patient while we create {} fake profiles....".format(n))
    fake = Faker()
    gender = ['Male', 'Female']
    sexo = ['bisexual', 'heterosexual', 'homosexual']
    city = ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria', 'Polokwane']
    gallery = ['dummy1.jpg', 'dummy2.jpg', 'dummy3.jpg', 'dummy4.jpg', 'dummy5.jpg', 'dummy6.jpg', 'dummy7.jpg', 'dummy8.jpg', 'dummy9.jpg']
    interests = ['Traveling', 'Animals', 'Technology', 'Sky-diving', 'Movies', 'Music', 'Cooking', 'Sports', 'Gaming']
    profile_pics = ['dummy1.png', 'dummy2.png', 'dummy3.png', 'dummy4.png', 'dummy5.png', 'dummy6.png', 'dummy7.png',
                    'dummy8.png', 'dummy9.png', 'dummy10.png']
    # setup toolbar
    # sys.stdout.write("[%s]" % (" " * n))
    # sys.stdout.flush()
    # sys.stdout.write("\b" * (n+1)) # return to start of line, after '['

    for i in tqdm(range(n)):
        # sys.stdout.write("#")
        # sys.stdout.flush()
        salt = bcrypt.gensalt()
        user_info = {'username': fake.user_name(), 'firstname': fake.first_name(), 'lastname': fake.last_name(),
                   'email': fake.email(), 'password': bcrypt.hashpw('Password1'.encode('utf-8'), salt),
                   'gender': random.choice(gender), 'sexual_orientation': random.choice(sexo), 'bio': fake.text(), 'interests': [],
                   'likes': [], 'liked': [], 'matched': [], 'blocked': [], 'views': [], 'rooms': {},
                   'fame-rating': 0, 'location': [], 'latlon': '', 'age': 18, 'image_name': 'dummy1.png', 'gallery': ['dummy1.jpg', 'dummy2.jpg', 'dummy3.jpg', 'dummy4.jpg'],
                   'token': secrets.token_hex(16), 'completed': 1, 'email_confirmed': 1, 'last-seen': datetime.utcnow(),
                   'notifications': []}

        max_interests = fake.random_int(3, 9)
        user_info['interests'] = random.sample(interests, max_interests)
        user_info['fame-rating'] = fake.random_int(5, 90)
        user_info['location'].append(''.join([str(fake.random_int(1, 500)), ' ', fake.word(), ' street']))
        user_info['location'].append(''.join([fake.word(), 'cliff']))
        user_info['location'].append(random.choice(city))
        user_info['location'].append('South Africa')
        user_info['latlon'] = fake.local_latlng(country_code="ZA", coords_only=True)
        user_info['age'] = fake.random_int(18, 80)
        user_info['image_name'] = random.choice(profile_pics)

        db.register_user(user_info)
    # sys.stdout.write("]\n")
    print("Done Creating Fake profiles")
    if not db.get_user({'username': "admin"}, {'username': 1}):
        print("Creating Fake Admin")
        salt = bcrypt.gensalt()
        Admin = {
            'username': 'admin',
            'firstname': 'Admin',
            'lastname': 'Admin',
            'email': 'admin@matcha.com',
            'password': bcrypt.hashpw('Admin1'.encode('utf-8'), salt),
            'gender': 'Male',
            'sexual_orientation': 'homosexual',
            'bio': 'Hi I am Root',
            'interests': ['Traveling', 'Animals', 'Technology'],
            'likes': [],
            'liked': [],
            'matched': [],
            'blocked': [],
            'views': [],
            'rooms': {},
            'fame-rating': 100,
            'location': ['84 Albertina Sisulu Street', 'Johannesburg', 'Johannesburg', 'South Africa'],
            'latlon': ['-24.19436', '29.00974'],
            'age': 21,
            'image_name': 'bob.jpg',
            'gallery': ['dummy1.jpg', 'dummy2.jpg', 'dummy3.jpg', 'dummy4.jpg'],
            'token': secrets.token_hex(16),
            'completed': 1,
            'email_confirmed': 1,
            'last-seen': datetime.utcnow(),
            'notifications': []
        }
        db.register_user(Admin)
        print("Done Creating Fake Admin")
