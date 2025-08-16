import pytest
from unittest.mock import patch
from app.repositories.todo_repository import TodoRepository

@pytest.fixture
def todo_repository():
    """Fixture to provide a TodoRepository instance with a mocked todos_db."""
    with patch('app.repositories.todo_repository.todos_db', new={}) as mock_todos_db:
        yield TodoRepository()

def test_get_todos_by_user_id(todo_repository):
    """Test retrieving todos for a specific user."""
    todo_repository.add_todo({"id": "1", "user_id": "user1", "description": "Task 1"})
    todo_repository.add_todo({"id": "2", "user_id": "user1", "description": "Task 2"})
    todo_repository.add_todo({"id": "3", "user_id": "user2", "description": "Task 3"})
    
    user1_todos = todo_repository.get_todos_by_user_id("user1")
    assert len(user1_todos) == 2
    assert {"id": "1", "user_id": "user1", "description": "Task 1"} in user1_todos
    assert {"id": "2", "user_id": "user1", "description": "Task 2"} in user1_todos

def test_get_todo_by_id(todo_repository):
    """Test retrieving a todo by ID."""
    todo_data = {"id": "1", "user_id": "user1", "description": "Test Todo"}
    todo_repository.add_todo(todo_data)
    todo = todo_repository.get_todo_by_id("1")
    assert todo == todo_data
    assert todo_repository.get_todo_by_id("nonexistent") is None

def test_add_todo(todo_repository):
    """Test adding a new todo."""
    todo_data = {"id": "1", "user_id": "user1", "description": "New Todo"}
    added_todo = todo_repository.add_todo(todo_data)
    assert added_todo == todo_data
    assert todo_repository.get_todo_by_id("1") == todo_data

def test_update_todo(todo_repository):
    """Test updating an existing todo."""
    todo_data = {"id": "1", "user_id": "user1", "description": "Old Desc", "status": "pending"}
    todo_repository.add_todo(todo_data)
    update_data = {"description": "New Desc", "status": "completed"}
    updated_todo = todo_repository.update_todo("1", update_data)
    assert updated_todo['description'] == "New Desc"
    assert updated_todo['status'] == "completed"
    assert todo_repository.get_todo_by_id("1") == updated_todo
    assert todo_repository.update_todo("nonexistent", {}) is None

def test_delete_todo(todo_repository):
    """Test deleting a todo."""
    todo_data = {"id": "1", "user_id": "user1", "description": "To Delete"}
    todo_repository.add_todo(todo_data)
    assert todo_repository.delete_todo("1") is True
    assert todo_repository.get_todo_by_id("1") is None
    assert todo_repository.delete_todo("nonexistent") is False
