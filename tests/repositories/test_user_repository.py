import pytest
from unittest.mock import MagicMock, patch
from app.repositories.user_repository import UserRepository
from app.repositories.dynamodb_models import UserModel
from pynamodb.exceptions import DoesNotExist, PutError, DeleteError, ScanError, QueryError

@pytest.fixture
def user_repository():
    """Fixture to provide a UserRepository instance."""
    return UserRepository()

def test_get_all_users(user_repository, mocker):
    """Test retrieving all users."""
    mock_user_model = MagicMock()
    mock_user_model.attribute_values = {"id": "1", "username": "user1"}
    mocker.patch('app.repositories.dynamodb_models.UserModel.scan', return_value=[mock_user_model])
    
    users = user_repository.get_all_users()
    assert len(users) == 1
    assert users[0]['username'] == 'user1'

def test_get_user_by_id(user_repository, mocker):
    """Test retrieving a user by ID."""
    mock_user_model = MagicMock()
    mock_user_model.attribute_values = {"id": "1", "username": "testuser"}
    mocker.patch('app.repositories.dynamodb_models.UserModel.get', return_value=mock_user_model)
    
    user = user_repository.get_user_by_id("1")
    assert user is not None
    assert user['username'] == 'testuser'

    mocker.patch('app.repositories.dynamodb_models.UserModel.get', side_effect=DoesNotExist)
    user = user_repository.get_user_by_id("nonexistent")
    assert user is None

def test_get_user_by_username(user_repository, mocker):
    """Test retrieving a user by username."""
    mock_user_model = MagicMock()
    mock_user_model.attribute_values = {"id": "1", "username": "testuser"}
    mocker.patch('app.repositories.dynamodb_models.UserModel.username_index.query', return_value=[mock_user_model])

    user = user_repository.get_user_by_username("testuser")
    assert user is not None
    assert user['username'] == 'testuser'

    mocker.patch('app.repositories.dynamodb_models.UserModel.username_index.query', return_value=[])
    user = user_repository.get_user_by_username("nonexistent")
    assert user is None

def test_add_user(user_repository, mocker):
    """Test adding a new user."""
    mocker.patch.object(user_repository, 'get_user_by_username', return_value=None)
    mock_save = mocker.patch('app.repositories.dynamodb_models.UserModel.save')
    
    user_data = {"username": "newuser", "email": "new@example.com", "password_hash": "hashed_password"}
    user, error = user_repository.add_user(user_data)
    
    assert error is None
    assert user is not None
    assert user['username'] == 'newuser'
    mock_save.assert_called_once()

def test_add_user_already_exists(user_repository, mocker):
    """Test adding a user that already exists."""
    mocker.patch.object(user_repository, 'get_user_by_username', return_value={"id": "1", "username": "existinguser"})
    
    user_data = {"username": "existinguser", "email": "new@example.com", "password_hash": "hashed_password"}
    user, error = user_repository.add_user(user_data)
    
    assert user is None
    assert error == "Username already exists"

def test_update_user(user_repository, mocker):
    """Test updating an existing user."""
    mock_user_model = MagicMock()
    mock_get = mocker.patch('app.repositories.dynamodb_models.UserModel.get', return_value=mock_user_model)
    mock_save = mocker.patch.object(mock_user_model, 'save')

    update_data = {"username": "newname"}
    updated_user = user_repository.update_user("1", update_data)
    
    assert updated_user is not None
    mock_get.assert_called_with("1")
    mock_save.assert_called_once()
    assert mock_user_model.username == "newname"

def test_delete_user(user_repository, mocker):
    """Test deleting a user."""
    mock_user_model = MagicMock()
    mocker.patch('app.repositories.dynamodb_models.UserModel.get', return_value=mock_user_model)
    mock_delete = mocker.patch.object(mock_user_model, 'delete')

    result = user_repository.delete_user("1")
    assert result is True
    mock_delete.assert_called_once()

    mocker.patch('app.repositories.dynamodb_models.UserModel.get', side_effect=DoesNotExist)
    result = user_repository.delete_user("nonexistent")
    assert result is False