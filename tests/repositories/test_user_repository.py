import pytest
from unittest.mock import patch
from app.repositories.user_repository import UserRepository

@pytest.fixture
def user_repository():
    """Fixture to provide a UserRepository instance with a mocked users_db."""
    with patch('app.repositories.user_repository.users_db', new={}) as mock_users_db:
        yield UserRepository()

def test_get_all_users(user_repository):
    """Test retrieving all users."""
    user_repository.add_user({"id": "1", "username": "user1"})
    user_repository.add_user({"id": "2", "username": "user2"})
    users = user_repository.get_all_users()
    assert len(users) == 2
    assert {"id": "1", "username": "user1"} in users
    assert {"id": "2", "username": "user2"} in users

def test_get_user_by_id(user_repository):
    """Test retrieving a user by ID."""
    user_data = {"id": "1", "username": "testuser"}
    user_repository.add_user(user_data)
    user = user_repository.get_user_by_id("1")
    assert user == user_data
    assert user_repository.get_user_by_id("nonexistent") is None

def test_get_user_by_username(user_repository):
    """Test retrieving a user by username."""
    user_data = {"id": "1", "username": "testuser"}
    user_repository.add_user(user_data)
    user = user_repository.get_user_by_username("testuser")
    assert user == user_data
    assert user_repository.get_user_by_username("nonexistent") is None

def test_add_user(user_repository):
    """Test adding a new user."""
    user_data = {"id": "1", "username": "newuser"}
    added_user = user_repository.add_user(user_data)
    assert added_user == user_data
    assert user_repository.get_user_by_id("1") == user_data

def test_update_user(user_repository):
    """Test updating an existing user."""
    user_data = {"id": "1", "username": "oldname", "email": "old@example.com"}
    user_repository.add_user(user_data)
    update_data = {"username": "newname", "email": "new@example.com"}
    updated_user = user_repository.update_user("1", update_data)
    assert updated_user['username'] == "newname"
    assert updated_user['email'] == "new@example.com"
    assert user_repository.get_user_by_id("1") == updated_user
    assert user_repository.update_user("nonexistent", {}) is None

def test_delete_user(user_repository):
    """Test deleting a user."""
    user_data = {"id": "1", "username": "todelete"}
    user_repository.add_user(user_data)
    assert user_repository.delete_user("1") is True
    assert user_repository.get_user_by_id("1") is None
    assert user_repository.delete_user("nonexistent") is False
