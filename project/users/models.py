from project import db, bcrypt
from flask import request, make_response
import jwt
from functools import wraps

import os

Followers = db.Table('followers',
                    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
                    )

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    username = db.Column(db.Text, unique=True)
    name = db.Column(db.Text)
    password = db.Column(db.Text)
    profile_img = db.Column(db.Text)
    messages = db.relationship(
        'Warbler',
        lazy='dynamic',
        backref=db.backref('user')
    )
    followed = db.relationship(
        'User',
        secondary=Followers,
        primaryjoin=(Followers.c.follower_id == id),
        secondaryjoin=(Followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def __init__(self, email, username, name, password, profile_img):
        self.email = email
        self.username = username
        self.name = name
        self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.profile_img = profile_img

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(Followers.c.followed_id == user.id).count() > 0


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return make_response('Token Required', 401, {'message' : 'Token is missing '})
            # return jsonify(message='Token is missing')
        try:
            data = jwt.decode(token.split(" ")[1], os.environ.get('SECRET_KEY'))
        except:
            return make_response('Invalid Token', 401, {'message' : 'Token is invalid'})
            # return jsonify(message='Token is invalid')
        return f(*args, **kwargs)
    return decorated