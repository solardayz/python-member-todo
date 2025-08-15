import pytest
import sys
sys.path.append('..') # Add parent directory to Python path
from app import app, users_db, add_dummy_data

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config["JWT_SECRET_KEY"] = "test-secret" # Use a test secret for JWT
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_db():
    # Clear the database before each test and re-add dummy data
    users_db.clear()
    add_dummy_data()
