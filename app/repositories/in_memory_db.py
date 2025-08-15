import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash

users_db = {}
todos_db = {}

def add_dummy_data():
    global users_db, todos_db
    users_db.clear()
    todos_db.clear()

    user1_id = str(uuid.uuid4())
    users_db[user1_id] = {
        "id": user1_id,
        "username": "test",
        "email": "test1@example.com",
        "password_hash": generate_password_hash("123456"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    user2_id = str(uuid.uuid4())
    users_db[user2_id] = {
        "id": user2_id,
        "username": "testuser2",
        "email": "test2@example.com",
        "password_hash": generate_password_hash("password123"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # Add dummy todos for testuser1
    todo1_id = str(uuid.uuid4())
    todos_db[todo1_id] = {
        "id": todo1_id,
        "user_id": user1_id,
        "description": "Buy groceries",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    todo2_id = str(uuid.uuid4())
    todos_db[todo2_id] = {
        "id": todo2_id,
        "user_id": user1_id,
        "description": "Walk the dog",
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # Add dummy todos for testuser2
    todo3_id = str(uuid.uuid4())
    todos_db[todo3_id] = {
        "id": todo3_id,
        "user_id": user2_id,
        "description": "Pay bills",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    print("Dummy data added to users_db and todos_db.")

# Call dummy data function on startup
add_dummy_data()
