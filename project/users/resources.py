from flask import Blueprint, make_response, jsonify, request
import jwt
import datetime
from flask_restful import Api, Resource, fields, marshal_with
from project.users.models import User
from project import db, bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
import os

user_blueprint = Blueprint('users', __name__)
users_api = Api(user_blueprint)

warbler_fields = {
    'id': fields.Integer,
    'message': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'img_url' : fields.String
}

followed_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String
}

user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'name': fields.String,
    'username': fields.String,
    'profile_img': fields.String,
    'msg_count': fields.Integer,
    'msgs': fields.List(fields.Nested(warbler_fields)),
    'followed': fields.List(fields.Nested(followed_fields))
}

# @users_api.resource('/')
class UsersAPI(Resource):
    @marshal_with(user_fields)
    def get(self): #get all users
        pass

    # @token_required
    def post(self): #create new user
        content = request.get_json()

        #check username and email uniqueness. ilike for case insensitive. The 'f' inf
        username_check = User.query.filter(User.username.ilike(f"%{content['username']}%")).first();
        email_check = User.query.filter(User.email.ilike(f"%{content['email']}%")).first();

        #Create form validator
        #Username - should check if username is available while user types.
            #email using regex
            #password (must be at least 8 characters)
            #username (must be at least 3 char)
            #name (must be at least 3 char)

        if username_check or email_check:
            result = 'User name ' if username_check else ''
            if email_check:
                if not result == '':
                    result += 'and '
                result += 'Email '

            result += 'already taken. Please try again.'
            return make_response(jsonify(error=result), 409)

        try:
            user = User(
                content['email'],
                content['username'],
                content['name'],
                content['password'], #hashed password created in models.py
                content['profile_img']
                )
            db.session.add(user)
            db.session.commit()
            token = jwt.encode({'user' : content['username'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=120)}, os.environ.get('SECRET_KEY'))
            return jsonify({'token' : token.decode('UTF-8')})

        except IntegrityError as e:
            return make_response('Cannot create user', 409)


class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, user_id): # get single user
        user = User.query.get_or_404(user_id)
        # msgCount = User.query.filter_by(id=user_id).first().messages.count()
        # msg_count = User.query.get_or_404(user_id).messages.count()
        # msg_count = user.messages.count()
        user.msg_count = user.messages.count()
        user.msgs = user.messages.order_by(desc('id')).all()
        return user

class Auth(Resource):
    def post(self):
        content = request.get_json()
        user = User.query.filter_by(username=content['username']).first()

        if user:
            authenticated_user=bcrypt.check_password_hash(user.password, content['password'])
            if authenticated_user:
                # https://www.youtube.com/watch?v=J5bIPtEbS0Q
                token = jwt.encode({'user' : user.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=120)}, os.environ.get('SECRET_KEY'))

                return jsonify({'token' : token.decode('UTF-8'), 'user_id' : user.id})
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login Required'})

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers-contacts-and-friends
class Follow(Resource):
    def post(self, user_id):
        pass

    def delete(self,user_id):
        pass

users_api.add_resource(UsersAPI, '')
users_api.add_resource(UserAPI, '/<string:user_id>')
users_api.add_resource(Auth, '/auth')
users_api.add_resource(Follow, '/<string:user_id>/follow')
