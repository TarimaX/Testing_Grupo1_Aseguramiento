import bleach
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from app import mongo, login

class User(UserMixin):
    def __init__(self, username, email, password_hash=None, id=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        return User(user['username'], user['email'], user['password_hash'], str(user['_id']))

    @staticmethod
    def get_by_username(username):
        user = mongo.db.users.find_one({"username": username})
        if not user:
            return None
        return User(user['username'], user['email'], user['password_hash'], str(user['_id']))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        if self.id is None:
            result = mongo.db.users.insert_one({
                'username': self.username,
                'email': self.email,
                'password_hash': self.password_hash
            })
            self.id = str(result.inserted_id)
        else:
            mongo.db.users.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': {
                    'username': self.username,
                    'email': self.email,
                    'password_hash': self.password_hash
                }}
            )

@login.user_loader
def load_user(user_id):
    return User.get(user_id)

class Task:
    def __init__(self, description, user_id, id=None):
        self.id = id
        self.description = bleach.clean(description)  # Sanitizar la descripción de la tarea
        self.user_id = user_id

    @staticmethod
    def get_all_by_user(user_id):
        tasks = mongo.db.tasks.find({"user_id": user_id})
        return [Task(task['description'], task['user_id'], str(task['_id'])) for task in tasks]

    @staticmethod
    def get(task_id):
        task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            return None
        return Task(task['description'], task['user_id'], str(task['_id']))

    def save(self):
        if self.id is None:
            result = mongo.db.tasks.insert_one({
                'description': self.description,
                'user_id': self.user_id
            })
            self.id = str(result.inserted_id)
        else:
            mongo.db.tasks.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': {
                    'description': self.description,
                    'user_id': self.user_id
                }}
            )

    def delete(self):
        mongo.db.tasks.delete_one({'_id': ObjectId(self.id)})
