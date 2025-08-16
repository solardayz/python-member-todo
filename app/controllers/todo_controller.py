from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.todo_service import TodoService

todos_ns = Namespace('todos', description='Todo list operations')

todo_service = TodoService()

todo_model = todos_ns.model('Todo', {
    'id': fields.String(readOnly=True, description='The unique identifier of a todo'),
    'user_id': fields.String(readOnly=True, description='The ID of the user who owns this todo'),
    'description': fields.String(required=True, description='The todo item description'),
    'status': fields.String(required=True, description='The status of the todo (e.g., pending, completed)'),
    'created_at': fields.String(readOnly=True, description='Timestamp of todo creation'),
    'updated_at': fields.String(readOnly=True, description='Timestamp of last update')
})

todo_input_model = todos_ns.model('TodoInput', {
    'description': fields.String(required=True, description='The todo item description'),
    'status': fields.String(description='The status of the todo (e.g., pending, completed)', default='pending')
})

@todos_ns.route('/')
class TodoList(Resource):
    @todos_ns.doc(security='apiKey')
    @jwt_required()
    @todos_ns.marshal_list_with(todo_model)
    def get(self):
        '''Lists all todos for the authenticated user'''
        current_user_id = get_jwt_identity()
        return todo_service.get_user_todos(current_user_id)

    @todos_ns.doc(security='apiKey')
    @jwt_required()
    @todos_ns.expect(todo_input_model, validate=True)
    @todos_ns.marshal_with(todo_model)
    @todos_ns.response(201, 'Todo successfully created')
    def post(self):
        '''Creates a new todo item for the authenticated user'''
        current_user_id = get_jwt_identity()
        data = request.json
        todo = todo_service.create_todo(current_user_id, data['description'], data.get('status', 'pending'))
        if todo is None:
            todos_ns.abort(500, "Failed to create todo item")
        return todo, 201

@todos_ns.route('/<string:todo_id>')
@todos_ns.param('todo_id', 'The todo identifier')
class Todo(Resource):
    @todos_ns.doc(security='apiKey')
    @jwt_required()
    @todos_ns.marshal_with(todo_model)
    @todos_ns.response(404, 'Todo not found')
    @todos_ns.response(403, 'Forbidden: You can only access your own todo')
    def get(self, todo_id):
        '''Fetches a todo given its identifier'''
        current_user_id = get_jwt_identity()
        todo = todo_service.get_todo_by_id_and_user(todo_id, current_user_id)
        if not todo:
            todos_ns.abort(404, "Todo not found or you don't have permission.")
        return todo

    @todos_ns.doc(security='apiKey')
    @jwt_required()
    @todos_ns.expect(todo_input_model, validate=True)
    @todos_ns.marshal_with(todo_model)
    @todos_ns.response(404, 'Todo not found')
    @todos_ns.response(403, 'Forbidden: You can only update your own todo')
    def put(self, todo_id):
        '''Updates a todo given its identifier'''
        current_user_id = get_jwt_identity()
        data = request.json
        todo = todo_service.update_todo(todo_id, current_user_id, data)
        if not todo:
            todos_ns.abort(404, "Todo not found or you don't have permission.")
        return todo

    @todos_ns.doc(security='apiKey')
    @jwt_required()
    @todos_ns.response(204, 'Todo successfully deleted')
    @todos_ns.response(404, 'Todo not found')
    @todos_ns.response(403, 'Forbidden: You can only delete your own todo')
    def delete(self, todo_id):
        '''Deletes a todo given its identifier'''
        current_user_id = get_jwt_identity()
        success = todo_service.delete_todo(todo_id, current_user_id)
        if not success:
            todos_ns.abort(404, "Todo not found or you don't have permission.")
        return '', 204
