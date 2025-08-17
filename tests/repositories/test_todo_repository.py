import pytest
from unittest.mock import MagicMock
from app.repositories.todo_repository import TodoRepository
from pynamodb.exceptions import DoesNotExist

@pytest.fixture
def todo_repository():
    """Fixture to provide a TodoRepository instance."""
    return TodoRepository()

def test_get_todos_by_user_id(todo_repository, mocker):
    """Test retrieving todos for a specific user."""
    mock_todo_model = MagicMock()
    mock_todo_model.attribute_values = {"id": "1", "user_id": "user1", "description": "Task 1"}
    mocker.patch('app.repositories.dynamodb_models.TodoModel.user_id_index.query', return_value=[mock_todo_model])
    
    todos = todo_repository.get_todos_by_user_id("user1")
    assert len(todos) == 1
    assert todos[0]['description'] == 'Task 1'

def test_get_todo_by_id_and_user(todo_repository, mocker):
    """Test retrieving a specific todo by id and user_id."""
    mock_todo_model = MagicMock()
    mock_todo_model.id = "1"
    mock_todo_model.user_id = "user1"
    mock_todo_model.attribute_values = {"id": "1", "user_id": "user1", "description": "Test Todo"}
    mocker.patch('app.repositories.dynamodb_models.TodoModel.get', return_value=mock_todo_model)

    # Correct user
    todo = todo_repository.get_todo_by_id_and_user("1", "user1")
    assert todo is not None
    assert todo['id'] == '1'

    # Incorrect user
    todo = todo_repository.get_todo_by_id_and_user("1", "user2")
    assert todo is None

    # Todo does not exist
    mocker.patch('app.repositories.dynamodb_models.TodoModel.get', side_effect=DoesNotExist)
    todo = todo_repository.get_todo_by_id_and_user("nonexistent", "user1")
    assert todo is None

def test_add_todo(todo_repository, mocker):
    """Test adding a new todo."""
    mock_save = mocker.patch('app.repositories.dynamodb_models.TodoModel.save')
    todo_data = {"user_id": "user1", "description": "New Todo", "status": "pending"}
    
    added_todo = todo_repository.add_todo(todo_data)
    
    assert added_todo is not None
    assert added_todo['description'] == "New Todo"
    mock_save.assert_called_once()

def test_update_todo(todo_repository, mocker):
    """Test updating an existing todo."""
    mock_todo_model = MagicMock()
    mock_todo_model.user_id = "user1"
    mock_get = mocker.patch('app.repositories.dynamodb_models.TodoModel.get', return_value=mock_todo_model)
    mock_save = mocker.patch.object(mock_todo_model, 'save')

    update_data = {"description": "New Desc", "status": "completed"}
    updated_todo = todo_repository.update_todo("1", "user1", update_data)

    assert updated_todo is not None
    mock_get.assert_called_with("1")
    mock_save.assert_called_once()
    assert mock_todo_model.description == "New Desc"

    # Test updating a todo that doesn't belong to the user
    mock_todo_model.user_id = "user2"
    updated_todo = todo_repository.update_todo("1", "user1", update_data)
    assert updated_todo is None

def test_delete_todo(todo_repository, mocker):
    """Test deleting a todo."""
    mock_todo_model = MagicMock()
    mock_todo_model.user_id = "user1"
    mocker.patch('app.repositories.dynamodb_models.TodoModel.get', return_value=mock_todo_model)
    mock_delete = mocker.patch.object(mock_todo_model, 'delete')

    # Correct user
    result = todo_repository.delete_todo("1", "user1")
    assert result is True
    mock_delete.assert_called_once()

    # Incorrect user
    mock_todo_model.user_id = "user2"
    result = todo_repository.delete_todo("1", "user1")
    assert result is False