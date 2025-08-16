from app.repositories.user_repository import UserRepository
from app.repositories.todo_repository import TodoRepository
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.todo_repo = TodoRepository()

    def signup_user(self, username, password, email=None):
        if self.user_repo.get_user_by_username(username):
            return None, "Username already exists"

        new_user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)
        
        user_data = {
            "id": new_user_id,
            "username": username,
            "email": email if email else f"{username}@example.com",
            "password_hash": hashed_password,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        user, error = self.user_repo.add_user(user_data)
        if error:
            return None, error
        return user, None

    def authenticate_user(self, username, password):
        user = self.user_repo.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None

    def get_user_profile(self, user_id):
        return self.user_repo.get_user_by_id(user_id)

    def update_user_profile(self, user_id, update_data):
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            return None
        
        user['username'] = update_data.get('username', user['username'])
        user['email'] = update_data.get('email', user['email'])
        user['updated_at'] = datetime.now().isoformat()
        self.user_repo.update_user(user_id, user)
        return user

    def delete_user(self, user_id):
        if not self.user_repo.get_user_by_id(user_id):
            return False
        
        # Delete associated todos
        user_todos = self.todo_repo.get_todos_by_user_id(user_id)
        for todo in user_todos:
            self.todo_repo.delete_todo(todo['id'])

        return self.user_repo.delete_user(user_id)

    def get_all_users(self):
        return self.user_repo.get_all_users()
