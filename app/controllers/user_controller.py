from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService

users_ns = Namespace('users', description='User profile operations')

user_service = UserService()

user_model = users_ns.model('User', {
    'id': fields.String(readOnly=True, description='The unique identifier of a user'),
    'username': fields.String(required=True, description='The user username'),
    'email': fields.String(required=True, description='The user email'),
    'created_at': fields.String(readOnly=True, description='Timestamp of user creation'),
    'updated_at': fields.String(readOnly=True, description='Timestamp of last update')
})

user_update_model = users_ns.model('UserUpdate', {
    'username': fields.String(description='The user username'),
    'email': fields.String(description='The user email')
})

@users_ns.route('/<string:user_id>')
@users_ns.param('user_id', 'The user identifier')
class User(Resource):
    @users_ns.doc(security='apiKey')
    @jwt_required()
    @users_ns.marshal_with(user_model)
    @users_ns.response(404, 'User not found')
    @users_ns.response(403, 'Forbidden: You can only access your own profile')
    def get(self, user_id):
        '''Fetches a user given its identifier'''
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            users_ns.abort(403, "Forbidden: You can only access your own profile")

        user = user_service.get_user_profile(user_id)
        if not user:
            users_ns.abort(404, "User not found")
        
        return user

    @users_ns.doc(security='apiKey')
    @jwt_required()
    @users_ns.expect(user_update_model, validate=True)
    @users_ns.marshal_with(user_model)
    @users_ns.response(404, 'User not found')
    @users_ns.response(403, 'Forbidden: You can only update your own profile')
    def put(self, user_id):
        '''Updates a user given its identifier'''
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            users_ns.abort(403, "Forbidden: You can only update your own profile")

        data = request.json
        user = user_service.update_user_profile(user_id, data)
        if not user:
            users_ns.abort(404, "User not found")
        
        return user

    @users_ns.doc(security='apiKey')
    @jwt_required()
    @users_ns.response(204, 'User successfully deleted')
    @users_ns.response(404, 'User not found')
    @users_ns.response(403, 'Forbidden: You can only delete your own profile')
    def delete(self, user_id):
        '''Deletes a user given its identifier'''
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            users_ns.abort(403, "Forbidden: You can only delete your own profile")

        success = user_service.delete_user(user_id)
        if not success:
            users_ns.abort(404, "User not found")
        
        return '', 204

@users_ns.route('/')
class UserList(Resource):
    @users_ns.marshal_list_with(user_model)
    def get(self):
        '''Lists all users'''
        return user_service.get_all_users()
