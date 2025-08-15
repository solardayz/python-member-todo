from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services.user_service import UserService

auth_ns = Namespace('auth', description='Authentication operations')

user_service = UserService()

user_auth_model = auth_ns.model('UserAuth', {
    'username': fields.String(required=True, description='The user username'),
    'password': fields.String(required=True, description='The user password', min_length=6)
})

@auth_ns.route('/signup')
class UserSignup(Resource):
    @auth_ns.expect(user_auth_model, validate=True)
    @auth_ns.response(201, 'User successfully created')
    @auth_ns.response(409, 'Username already exists')
    def post(self):
        '''Creates a new user'''
        data = request.json
        username = data['username']
        password = data['password']

        user, error = user_service.signup_user(username, password)
        if error:
            auth_ns.abort(409, error)
        
        return {'message': 'User created successfully', 'user_id': user['id']}, 201

@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(user_auth_model, validate=True)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        '''Logs in a user and returns an access token'''
        data = request.json
        username = data['username']
        password = data['password']

        user = user_service.authenticate_user(username, password)
        if user:
            access_token = create_access_token(identity=user['id'])
            return {'access_token': access_token}, 200
        else:
            auth_ns.abort(401, 'Invalid username or password')
