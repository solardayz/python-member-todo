from app.repositories.in_memory_db import users_db

class UserRepository:
    def get_all_users(self):
        return list(users_db.values())

    def get_user_by_id(self, user_id):
        return users_db.get(user_id)

    def get_user_by_username(self, username):
        for user in users_db.values():
            if user['username'] == username:
                return user
        return None

    def add_user(self, user_data):
        users_db[user_data['id']] = user_data
        return user_data

    def update_user(self, user_id, user_data):
        if user_id in users_db:
            users_db[user_id].update(user_data)
            return users_db[user_id]
        return None

    def delete_user(self, user_id):
        if user_id in users_db:
            del users_db[user_id]
            return True
        return False
