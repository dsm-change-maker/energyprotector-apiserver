from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask import Flask
import threading
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import config


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():

    app = Flask(__name__)

    app.config.from_object(config)

    from .api import device_api
    from .api import raspberry_api
    app.register_blueprint(device_api.bp)
    app.register_blueprint(raspberry_api.bp)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from . import models

    return app
