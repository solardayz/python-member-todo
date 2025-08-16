import pytest
from unittest.mock import MagicMock, patch
from app.services.user_service import UserService

@pytest.fixture
def user_service():
    """Fixture to provide a UserService instance with mocked dependencies."""
    with patch('app.services.user_service.UserRepository') as MockUserRepository, \
         patch('app.services.user_service.TodoRepository') as MockTodoRepository:
        
        # Configure the mock user repository
        mock_user_repo_instance = MockUserRepository.return_value
        mock_user_repo_instance.get_user_by_username.return_value = None # Default: username does not exist
        mock_user_repo_instance.add_user.return_value = None # add_user doesn't return anything

        service = UserService()
        service.user_repo = mock_user_repo_instance # Ensure the service uses our mock
        service.todo_repo = MockTodoRepository.return_value # Ensure the service uses our mock
        yield service
        
def test_signup_user_success(user_service):
    """Test successful user signup."""
    username = "testuser"
    password = "password123"
    email = "test@example.com"

    with patch('app.services.user_service.generate_password_hash', return_value="hashed_password"):
        user_data, error = user_service.signup_user(username, password, email)

        assert error is None
        assert user_data is not None
        assert user_data['username'] == username
        assert user_data['email'] == email
        assert user_data['password_hash'] == "hashed_password"
        user_service.user_repo.add_user.assert_called_once()
        user_service.user_repo.get_user_by_username.assert_called_once_with(username)

def test_signup_user_username_exists(user_service):
    """Test user signup when username already exists."""
    username = "existinguser"
    password = "password123"

    # Configure mock to simulate existing user
    user_service.user_repo.get_user_by_username.return_value = {"username": username}

    user_data, error = user_service.signup_user(username, password)

    assert user_data is None
    assert error == "Username already exists"
    user_service.user_repo.add_user.assert_not_called()
    user_service.user_repo.get_user_by_username.assert_called_once_with(username)

def test_authenticate_user_success(user_service):
    """Test successful user authentication."""
    username = "authuser"
    password = "authpassword"
    hashed_password = "hashed_authpassword"
    
    mock_user = {"username": username, "password_hash": hashed_password}
    user_service.user_repo.get_user_by_username.return_value = mock_user

    with patch('app.services.user_service.check_password_hash', return_value=True):
        authenticated_user = user_service.authenticate_user(username, password)
        assert authenticated_user == mock_user
        user_service.user_repo.get_user_by_username.assert_called_once_with(username)

def test_authenticate_user_fail_wrong_password(user_service):
    """Test user authentication with wrong password."""
    username = "authuser"
    password = "wrongpassword"
    hashed_password = "hashed_authpassword"
    
    mock_user = {"username": username, "password_hash": hashed_password}
    user_service.user_repo.get_user_by_username.return_value = mock_user

    with patch('app.services.user_service.check_password_hash', return_value=False):
        authenticated_user = user_service.authenticate_user(username, password)
        assert authenticated_user is None
        user_service.user_repo.get_user_by_username.assert_called_once_with(username)

def test_authenticate_user_fail_user_not_found(user_service):
    """Test user authentication when user is not found."""
    username = "nonexistentuser"
    password = "anypassword"
    
    user_service.user_repo.get_user_by_username.return_value = None

    authenticated_user = user_service.authenticate_user(username, password)
    assert authenticated_user is None
    user_service.user_repo.get_user_by_username.assert_called_once_with(username)
