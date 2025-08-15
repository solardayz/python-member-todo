import pytest
import json
from app import app, users_db, todos_db, add_dummy_data
from flask_jwt_extended import create_access_token

@pytest.fixture(autouse=True)
def reset_db_for_tests():
    # This fixture will run before each test to ensure a clean state
    users_db.clear()
    todos_db.clear()
    add_dummy_data()

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config["JWT_SECRET_KEY"] = "test-secret" # Use a test secret for JWT
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(test_client):
    # Login a dummy user and get a token
    response = test_client.post(
        '/auth/login',
        data=json.dumps({'username': 'testuser1', 'password': 'password123'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    access_token = response.json['access_token']
    return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def auth_headers_user2(test_client):
    # Login testuser2 and get a token
    response = test_client.post(
        '/auth/login',
        data=json.dumps({'username': 'testuser2', 'password': 'password123'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    access_token = response.json['access_token']
    return {'Authorization': f'Bearer {access_token}'}


# --- Auth Tests ---

def test_signup_success(test_client):
    response = test_client.post(
        '/auth/signup',
        data=json.dumps({'username': 'newuser', 'password': 'newpassword'}),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert 'message' in response.json
    assert 'user_id' in response.json
    assert response.json['message'] == 'User created successfully'
    assert 'newuser' in [user['username'] for user in users_db.values()]

def test_signup_duplicate_username(test_client):
    response = test_client.post(
        '/auth/signup',
        data=json.dumps({'username': 'testuser1', 'password': 'anotherpass'}),
        content_type='application/json'
    )
    assert response.status_code == 409
    assert 'Username ' in response.json['message']

def test_login_success(test_client):
    response = test_client.post(
        '/auth/login',
        data=json.dumps({'username': 'testuser1', 'password': 'password123'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(test_client):
    response = test_client.post(
        '/auth/login',
        data=json.dumps({'username': 'testuser1', 'password': 'wrongpass'}),
        content_type='application/json'
    )
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid username or password'

    response = test_client.post(
        '/auth/login',
        data=json.dumps({'username': 'nonexistent', 'password': 'password123'}),
        content_type='application/json'
    )
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid username or password'

# --- User Management Tests ---

def test_get_all_users(test_client):
    response = test_client.get('/users/')
    assert response.status_code == 200
    assert len(response.json) == 2 # Initial dummy users
    assert 'testuser1' in [user['username'] for user in response.json]

def test_get_user_profile_success(test_client, auth_headers):
    # Find testuser1's ID
    testuser1_id = None
    for user_id, user_data in users_db.items():
        if user_data['username'] == 'testuser1':
            testuser1_id = user_id
            break
    assert testuser1_id is not None

    response = test_client.get(f'/users/{testuser1_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['username'] == 'testuser1'

def test_get_user_profile_unauthorized(test_client):
    # Find testuser1's ID
    testuser1_id = None
    for user_id, user_data in users_db.items():
        if user_data['username'] == 'testuser1':
            testuser1_id = user_id
            break
    assert testuser1_id is not None

    response = test_client.get(f'/users/{testuser1_id}') # No headers
    assert response.status_code == 401
    assert response.json['msg'] == 'Missing Authorization Header'

def test_get_user_profile_forbidden(test_client, auth_headers):
    # Find testuser2's ID (different from auth_headers user)
    testuser2_id = None
    for user_id, user_data in users_db.items():
        if user_data['username'] == 'testuser2':
            testuser2_id = user_id
            break
    assert testuser2_id is not None

    response = test_client.get(f'/users/{testuser2_id}', headers=auth_headers)
    assert response.status_code == 403
    assert response.json['message'] == 'Forbidden: You can only access your own profile'

def test_update_user_profile_success(test_client, auth_headers):
    # Find testuser1's ID
    testuser1_id = None
    for user_id, user_data in users_db.items():
        if user_data['username'] == 'testuser1':
            testuser1_id = user_id
            break
    assert testuser1_id is not None

    update_data = {'username': 'updated_testuser1', 'email': 'updated1@example.com'}
    response = test_client.put(
        f'/users/{testuser1_id}',
        data=json.dumps(update_data),
        content_type='application/json',
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json['username'] == 'updated_testuser1'
    assert response.json['email'] == 'updated1@example.com'
    assert users_db[testuser1_id]['username'] == 'updated_testuser1'

def test_update_user_profile_forbidden(test_client, auth_headers):
    # Find testuser2's ID
    testuser2_id = None
    for user_id, user_data in users_db.items():
        if user_data['username'] == 'testuser2':
            testuser2_id = user_id
            break
    assert testuser2_id is not None

    update_data = {'username': 'hacker_user'}
    response = test_client.put(
        f'/users/{testuser2_id}',
        data=json.dumps(update_data),
        content_type='application/json',
        headers=auth_headers
    )
    assert response.status_code == 403
    assert response.json['message'] == 'Forbidden: You can only update your own profile'

def test_delete_user_profile_success(test_client, auth_headers):
    # Find testuser1's ID
    testuser1_id = None
    for user_id, user_data in users_db.items():
        if user_data['username'] == 'testuser1':
            testuser1_id = user_id
            break
    assert testuser1_id is not None

    response = test_client.delete(f'/users/{testuser1_id}', headers=auth_headers)
    assert response.status_code == 204
    assert testuser1_id not in users_db

def test_delete_user_profile_forbidden(test_client, auth_headers):
    # Find testuser2's ID
    testuser2_id = None
    for user_id, user_data in users_db.items():
        if user_data['username'] == 'testuser2':
            testuser2_id = user_id
            break
    assert testuser2_id is not None

    response = test_client.delete(f'/users/{testuser2_id}', headers=auth_headers)
    assert response.status_code == 403
    assert response.json['message'] == 'Forbidden: You can only delete your own profile'

# --- Todo Tests ---

def test_create_todo_success(test_client, auth_headers):
    todo_data = {'description': 'New test todo', 'status': 'pending'}
    response = test_client.post(
        '/todos/',
        data=json.dumps(todo_data),
        content_type='application/json',
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json['description'] == 'New test todo'
    assert response.json['status'] == 'pending'
    assert response.json['user_id'] == users_db[[k for k,v in users_db.items() if v['username'] == 'testuser1'][0]]['id']

def test_get_user_todos_success(test_client, auth_headers):
    response = test_client.get('/todos/', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json) == 2 # testuser1 has 2 dummy todos
    assert 'Buy groceries' in [todo['description'] for todo in response.json]

def test_get_single_todo_success(test_client, auth_headers):
    # Find a todo for testuser1
    testuser1_id = [k for k,v in users_db.items() if v['username'] == 'testuser1'][0]
    todo_id = [k for k,v in todos_db.items() if v['user_id'] == testuser1_id][0]

    response = test_client.get(f'/todos/{todo_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['id'] == todo_id
    assert response.json['user_id'] == testuser1_id

def test_get_single_todo_forbidden(test_client, auth_headers):
    # Find a todo for testuser2
    testuser2_id = [k for k,v in users_db.items() if v['username'] == 'testuser2'][0]
    todo_id = [k for k,v in todos_db.items() if v['user_id'] == testuser2_id][0]

    response = test_client.get(f'/todos/{todo_id}', headers=auth_headers)
    assert response.status_code == 403
    assert response.json['message'] == 'Forbidden: You can only access your own todo'

def test_update_todo_success(test_client, auth_headers):
    # Find a todo for testuser1
    testuser1_id = [k for k,v in users_db.items() if v['username'] == 'testuser1'][0]
    todo_id = [k for k,v in todos_db.items() if v['user_id'] == testuser1_id][0]

    update_data = {'description': 'Updated todo description', 'status': 'completed'}
    response = test_client.put(
        f'/todos/{todo_id}',
        data=json.dumps(update_data),
        content_type='application/json',
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json['description'] == 'Updated todo description'
    assert response.json['status'] == 'completed'
    assert todos_db[todo_id]['description'] == 'Updated todo description'

def test_update_todo_forbidden(test_client, auth_headers):
    # Find a todo for testuser2
    testuser2_id = [k for k,v in users_db.items() if v['username'] == 'testuser2'][0]
    todo_id = [k for k,v in todos_db.items() if v['user_id'] == testuser2_id][0]

    update_data = {'description': 'Hacked todo'}
    response = test_client.put(
        f'/todos/{todo_id}',
        data=json.dumps(update_data),
        content_type='application/json',
        headers=auth_headers
    )
    assert response.status_code == 403
    assert response.json['message'] == 'Forbidden: You can only update your own todo'

def test_delete_todo_success(test_client, auth_headers):
    # Find a todo for testuser1
    testuser1_id = [k for k,v in users_db.items() if v['username'] == 'testuser1'][0]
    todo_id = [k for k,v in todos_db.items() if v['user_id'] == testuser1_id][0]

    response = test_client.delete(f'/todos/{todo_id}', headers=auth_headers)
    assert response.status_code == 204
    assert todo_id not in todos_db

def test_delete_todo_forbidden(test_client, auth_headers):
    # Find a todo for testuser2
    testuser2_id = [k for k,v in users_db.items() if v['username'] == 'testuser2'][0]
    todo_id = [k for k,v in todos_db.items() if v['user_id'] == testuser2_id][0]

    response = test_client.delete(f'/todos/{todo_id}', headers=auth_headers)
    assert response.status_code == 403
    assert response.json['message'] == 'Forbidden: You can only delete your own todo'