from app.repositories.in_memory_db import todos_db

class TodoRepository:
    def get_todos_by_user_id(self, user_id):
        return [todo for todo_id, todo in todos_db.items() if todo['user_id'] == user_id]

    def get_todo_by_id(self, todo_id):
        return todos_db.get(todo_id)

    def add_todo(self, todo_data):
        todos_db[todo_data['id']] = todo_data
        return todo_data

    def update_todo(self, todo_id, todo_data):
        if todo_id in todos_db:
            todos_db[todo_id].update(todo_data)
            return todos_db[todo_id]
        return None

    def delete_todo(self, todo_id):
        if todo_id in todos_db:
            del todos_db[todo_id]
            return True
        return False
