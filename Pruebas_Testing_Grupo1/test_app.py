import unittest
from app import create_app, mongo
from app.models import User, Task
from app.forms import LoginForm, RegistrationForm, TaskForm
from flask import url_for
from flask_login import current_user

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        with self.app.app_context():
            mongo.cx.drop_database('test_todo_app')
            self.user = User(username='testuser', email='test@example.com')
            self.user.set_password('password')
            self.user.save()

    def tearDown(self):
        mongo.cx.drop_database('test_todo_app')
        self.app_context.pop()

    def test_login(self):
        response = self.client.post(url_for('main.login'), data={
            'username': 'testuser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 302)

    def test_register(self):
        response = self.client.post(url_for('main.register'), data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password',
            'password2': 'password'
        })
        self.assertEqual(response.status_code, 302)

class TaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        with self.app.app_context():
            mongo.cx.drop_database('test_todo_app')
            self.user = User(username='testuser', email='test@example.com')
            self.user.set_password('password')
            self.user.save()
            login_user(self.user)

    def tearDown(self):
        mongo.cx.drop_database('test_todo_app')
        self.app_context.pop()

    def test_add_task(self):
        response = self.client.post(url_for('main.add_task'), data={'description': 'New Task'})
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            tasks = Task.get_all_by_user(self.user.id)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0].description, 'New Task')

    def test_edit_task(self):
        with self.app.app_context():
            task = Task(description='Old Task', user_id=self.user.id)
            task.save()
        response = self.client.post(url_for('main.edit_task', id=task.id), data={'description': 'Updated Task'})
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            updated_task = Task.get(task.id)
            self.assertEqual(updated_task.description, 'Updated Task')

    def test_delete_task(self):
        with self.app.app_context():
            task = Task(description='Task to delete', user_id=self.user.id)
            task.save()
        response = self.client.post(url_for('main.delete_task', id=task.id))
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            deleted_task = Task.get(task.id)
            self.assertIsNone(deleted_task)

if __name__ == '__main__':
    unittest.main()
