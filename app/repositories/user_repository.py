from app.repositories.dynamodb_models import UserModel
from pynamodb.exceptions import DoesNotExist, GetError, PutError, DeleteError, ScanError, QueryError
import uuid

class UserRepository:
    def get_all_users(self):
        try:
            # Scan is generally not recommended for large tables in production
            # but for a simple list all users, it works.
            # Consider pagination or other query patterns for large datasets.
            users = []
            for user_model in UserModel.scan():
                users.append(user_model.attribute_values)
            return users
        except ScanError as e:
            print(f"Error scanning users: {e}")
            return []

    def get_user_by_id(self, user_id):
        try:
            user_model = UserModel.get(user_id)
            return user_model.attribute_values
        except DoesNotExist:
            return None
        except GetError as e:
            print(f"Error getting user by ID: {e}")
            return None

    def get_user_by_username(self, username):
        try:
            # Use the GSI for efficient lookup by username
            for user_model in UserModel.username_index.query(username):
                return user_model.attribute_values
            return None
        except QueryError as e:
            print(f"Error querying for username: {e}")
            return None

    def add_user(self, user_data):
        try:
            # Check if username already exists before adding
            if self.get_user_by_username(user_data['username']):
                return None, "Username already exists"

            user_id = str(uuid.uuid4())
            # Create a dictionary for model attributes, ensuring 'id' is set only once
            model_attributes = {
                "id": user_id,
                "username": user_data['username'],
                "email": user_data['email'],
                "password_hash": user_data['password_hash'] # Store hashed password
            }
            user_model = UserModel(**model_attributes)
            user_model.save()
            return user_model.attribute_values, None
        except PutError as e:
            print(f"Error adding user: {e}")
            return None, "Failed to add user"

    def update_user(self, user_id, user_data):
        try:
            user_model = UserModel.get(user_id)
            for key, value in user_data.items():
                setattr(user_model, key, value)
            user_model.save()
            return user_model.attribute_values
        except DoesNotExist:
            return None
        except (GetError, PutError) as e:
            print(f"Error updating user: {e}")
            return None

    def delete_user(self, user_id):
        try:
            user_model = UserModel.get(user_id)
            user_model.delete()
            return True
        except DoesNotExist:
            return False
        except DeleteError as e:
            print(f"Error deleting user: {e}")
            return False