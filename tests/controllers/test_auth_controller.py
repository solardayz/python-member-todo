import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from flask_restx import Api
from app.controllers.auth_controller import auth_ns

# Create a test Flask app and API
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    api = Api(app)
    api.add_namespace(auth_ns)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_user_service():
    with patch('app.controllers.auth_controller.user_service') as mock_service:
        yield mock_service

@pytest.fixture
def mock_create_access_token():
    with patch('app.controllers.auth_controller.create_access_token') as mock_token:
        mock_token.return_value = "mock_access_token"
        yield mock_token

def test_signup_user_success(client, mock_user_service):
    """Test successful user signup via the API."""
    mock_user_service.signup_user.return_value = ({'id': '123', 'username': 'testuser'}, None)
    
    response = client.post(
        '/auth/signup',
        data=json.dumps({'username': 'testuser', 'password': 'password123'}),
        content_type='application/json'
    )

    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully'
    assert response.json['user_id'] == '123'
    mock_user_service.signup_user.assert_called_once_with('testuser', 'password123')

def test_signup_user_username_exists(client, mock_user_service):
    """Test user signup when username already exists."""
    mock_user_service.signup_user.return_value = (None, 'Username already exists')

    response = client.post(
        '/auth/signup',
        data=json.dumps({'username': 'existinguser', 'password': 'password123'}),
        content_type='application/json'
    )

    assert response.status_code == 409
    assert 'Username already exists' in response.json['message']
    mock_user_service.signup_user.assert_called_once_with('existinguser', 'password123')

def test_login_user_success(client, mock_user_service, mock_create_access_token):
    """Test successful user login via the API."""
    mock_user_service.authenticate_user.return_value = {'id': '123', 'username': 'testuser'}

    response = client.post(
        '/auth/login',
        data=json.dumps({'username': 'testuser', 'password': 'password123'}),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.json['access_token'] == 'mock_access_token'
    mock_user_service.authenticate_user.assert_called_once_with('testuser', 'password123')
    mock_create_access_token.assert_called_once_with(identity='123')

def test_login_user_invalid_credentials(client, mock_user_service):
    """Test user login with invalid credentials."""
    mock_user_service.authenticate_user.return_value = None

    response = client.post(
        '/auth/login',
        data=json.dumps({'username': 'wronguser', 'password': 'wrongpass'}),
        content_type='application/json'
    )

    assert response.status_code == 401
    assert 'Invalid username or password' in response.json['message']
    mock_user_service.authenticate_user.assert_called_once_with('wronguser', 'wrongpass')
