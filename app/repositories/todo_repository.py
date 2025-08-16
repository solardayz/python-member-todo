from app.repositories.dynamodb_models import TodoModel, TodoUserIdIndex
from pynamodb.exceptions import DoesNotExist, GetError, PutError, DeleteError, QueryError
import uuid

class TodoRepository:
    def get_todos_by_user_id(self, user_id):
        try:
            # Use the GSI to query todos by user_id
            todos = []
            for todo_model in TodoModel.user_id_index.query(user_id):
                todos.append(todo_model.attribute_values)
            return todos
        except QueryError as e:
            print(f"Error querying todos by user ID: {e}")
            return []

    def get_todo_by_id(self, todo_id):
        # This method is not used directly by the service layer with user_id
        # The service layer uses get_todo_by_id_and_user
        try:
            todo_model = TodoModel.get(todo_id)
            return todo_model.attribute_values
        except DoesNotExist:
            return None
        except GetError as e:
            print(f"Error getting todo by ID: {e}")
            return None

    def get_todo_by_id_and_user(self, todo_id, user_id):
        try:
            # Get by primary key (id) and then verify user_id
            todo_model = TodoModel.get(todo_id)
            if todo_model.user_id == user_id:
                return todo_model.attribute_values
            return None # Todo found but doesn't belong to the user
        except DoesNotExist:
            return None
        except GetError as e:
            print(f"Error getting todo by ID and user: {e}")
            return None

    def add_todo(self, todo_data):
        try:
            todo_id = str(uuid.uuid4())
            # Create a dictionary for model attributes, ensuring 'id' is set only once
            model_attributes = {
                "id": todo_id,
                "user_id": todo_data['user_id'],
                "description": todo_data['description'],
                "status": todo_data['status']
            }
            todo_model = TodoModel(**model_attributes)
            todo_model.save()
            return todo_model.attribute_values
        except PutError as e:
            print(f"Error adding todo: {e}")
            return None

    def update_todo(self, todo_id, user_id, todo_data):
        try:
            todo_model = TodoModel.get(todo_id)
            if todo_model.user_id != user_id:
                return None # Todo found but doesn't belong to the user

            for key, value in todo_data.items():
                setattr(todo_model, key, value)
            todo_model.save()
            return todo_model.attribute_values
        except DoesNotExist:
            return None
        except (GetError, PutError) as e:
            print(f"Error updating todo: {e}")
            return None

    def delete_todo(self, todo_id, user_id):
        try:
            todo_model = TodoModel.get(todo_id)
            if todo_model.user_id != user_id:
                return False # Todo found but doesn't belong to the user

            todo_model.delete()
            return True
        except DoesNotExist:
            return False
        except DeleteError as e:
            print(f"Error deleting todo: {e}")
            return False