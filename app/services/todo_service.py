from app.repositories.todo_repository import TodoRepository
import uuid
from datetime import datetime

class TodoService:
    def __init__(self):
        self.todo_repo = TodoRepository()

    def create_todo(self, user_id, description, status='pending'):
        new_todo_id = str(uuid.uuid4())
        todo_data = {
            "id": new_todo_id,
            "user_id": user_id,
            "description": description,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return self.todo_repo.add_todo(todo_data)

    def get_user_todos(self, user_id):
        return self.todo_repo.get_todos_by_user_id(user_id)

    def get_todo_by_id_and_user(self, todo_id, user_id):
        todo = self.todo_repo.get_todo_by_id(todo_id)
        if todo and todo['user_id'] == user_id:
            return todo
        return None

    def update_todo(self, todo_id, user_id, update_data):
        todo = self.todo_repo.get_todo_by_id(todo_id)
        if not todo or todo['user_id'] != user_id:
            return None
        
        todo['description'] = update_data.get('description', todo['description'])
        todo['status'] = update_data.get('status', todo['status'])
        todo['updated_at'] = datetime.now().isoformat()
        return self.todo_repo.update_todo(todo_id, todo)

    def delete_todo(self, todo_id, user_id):
        todo = self.todo_repo.get_todo_by_id(todo_id)
        if not todo or todo['user_id'] != user_id:
            return False
        
        return self.todo_repo.delete_todo(todo_id)
