import pytest
from unittest.mock import MagicMock, patch
from app.services.todo_service import TodoService

@pytest.fixture
def todo_service():
    """Fixture to provide a TodoService instance with mocked dependencies."""
    with patch('app.services.todo_service.TodoRepository') as MockTodoRepository:
        mock_todo_repo_instance = MockTodoRepository.return_value
        service = TodoService()
        service.todo_repo = mock_todo_repo_instance
        yield service

def test_create_todo(todo_service):
    """Test creating a new todo item."""
    user_id = "user123"
    description = "Buy groceries"
    
    todo_service.todo_repo.add_todo.return_value = {
        "id": "some_uuid", "user_id": user_id, "description": description, "status": "pending"
    }

    todo = todo_service.create_todo(user_id, description)

    assert todo is not None
    assert todo['user_id'] == user_id
    assert todo['description'] == description
    assert todo['status'] == "pending"
    todo_service.todo_repo.add_todo.assert_called_once()

def test_get_user_todos(todo_service):
    """Test retrieving all todos for a specific user."""
    user_id = "user123"
    mock_todos = [
        {"id": "todo1", "user_id": user_id, "description": "Task 1"},
        {"id": "todo2", "user_id": user_id, "description": "Task 2"}
    ]
    todo_service.todo_repo.get_todos_by_user_id.return_value = mock_todos

    todos = todo_service.get_user_todos(user_id)

    assert todos == mock_todos
    todo_service.todo_repo.get_todos_by_user_id.assert_called_once_with(user_id)

def test_get_todo_by_id_and_user_success(todo_service):
    """Test retrieving a specific todo by ID and user ID (success case)."""
    todo_id = "todo123"
    user_id = "user123"
    mock_todo = {"id": todo_id, "user_id": user_id, "description": "Test Todo"}
    todo_service.todo_repo.get_todo_by_id.return_value = mock_todo

    todo = todo_service.get_todo_by_id_and_user(todo_id, user_id)

    assert todo == mock_todo
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)

def test_get_todo_by_id_and_user_not_found(todo_service):
    """Test retrieving a specific todo by ID (not found)."""
    todo_id = "nonexistent_todo"
    user_id = "user123"
    todo_service.todo_repo.get_todo_by_id.return_value = None

    todo = todo_service.get_todo_by_id_and_user(todo_id, user_id)

    assert todo is None
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)

def test_get_todo_by_id_and_user_wrong_user(todo_service):
    """Test retrieving a specific todo by ID (wrong user)."""
    todo_id = "todo123"
    user_id = "user123"
    wrong_user_id = "user456"
    mock_todo = {"id": todo_id, "user_id": wrong_user_id, "description": "Test Todo"}
    todo_service.todo_repo.get_todo_by_id.return_value = mock_todo

    todo = todo_service.get_todo_by_id_and_user(todo_id, user_id)

    assert todo is None
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)

def test_update_todo_success(todo_service):
    """Test updating an existing todo item (success case)."""
    todo_id = "todo123"
    user_id = "user123"
    update_data = {"description": "Updated description", "status": "completed"}
    original_todo = {"id": todo_id, "user_id": user_id, "description": "Old description", "status": "pending"}
    
    todo_service.todo_repo.get_todo_by_id.return_value = original_todo
    todo_service.todo_repo.update_todo.return_value = {**original_todo, **update_data}

    updated_todo = todo_service.update_todo(todo_id, user_id, update_data)

    assert updated_todo is not None
    assert updated_todo['description'] == update_data['description']
    assert updated_todo['status'] == update_data['status']
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)
    todo_service.todo_repo.update_todo.assert_called_once()

def test_update_todo_not_found(todo_service):
    """Test updating a todo item that does not exist."""
    todo_id = "nonexistent_todo"
    user_id = "user123"
    update_data = {"description": "Updated description"}
    todo_service.todo_repo.get_todo_by_id.return_value = None

    updated_todo = todo_service.update_todo(todo_id, user_id, update_data)

    assert updated_todo is None
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)
    todo_service.todo_repo.update_todo.assert_not_called()

def test_update_todo_wrong_user(todo_service):
    """Test updating a todo item by a wrong user."""
    todo_id = "todo123"
    user_id = "user123"
    wrong_user_id = "user456"
    update_data = {"description": "Updated description"}
    original_todo = {"id": todo_id, "user_id": wrong_user_id, "description": "Old description", "status": "pending"}
    todo_service.todo_repo.get_todo_by_id.return_value = original_todo

    updated_todo = todo_service.update_todo(todo_id, user_id, update_data)

    assert updated_todo is None
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)
    todo_service.todo_repo.update_todo.assert_not_called()

def test_delete_todo_success(todo_service):
    """Test deleting a todo item (success case)."""
    todo_id = "todo123"
    user_id = "user123"
    mock_todo = {"id": todo_id, "user_id": user_id, "description": "Test Todo"}
    todo_service.todo_repo.get_todo_by_id.return_value = mock_todo
    todo_service.todo_repo.delete_todo.return_value = True

    result = todo_service.delete_todo(todo_id, user_id)

    assert result is True
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)
    todo_service.todo_repo.delete_todo.assert_called_once_with(todo_id)

def test_delete_todo_not_found(todo_service):
    """Test deleting a todo item that does not exist."""
    todo_id = "nonexistent_todo"
    user_id = "user123"
    todo_service.todo_repo.get_todo_by_id.return_value = None

    result = todo_service.delete_todo(todo_id, user_id)

    assert result is False
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)
    todo_service.todo_repo.delete_todo.assert_not_called()

def test_delete_todo_wrong_user(todo_service):
    """Test deleting a todo item by a wrong user."""
    todo_id = "todo123"
    user_id = "user123"
    wrong_user_id = "user456"
    mock_todo = {"id": todo_id, "user_id": wrong_user_id, "description": "Test Todo"}
    todo_service.todo_repo.get_todo_by_id.return_value = mock_todo

    result = todo_service.delete_todo(todo_id, user_id)

    assert result is False
    todo_service.todo_repo.get_todo_by_id.assert_called_once_with(todo_id)
    todo_service.todo_repo.delete_todo.assert_not_called()
