from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from config import Config

mongo = PyMongo()
login = LoginManager()
login.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    login.init_app(app)

    from app import routes, models
    app.register_blueprint(routes.bp)

    return app
