"""
 Copyright 2019 Frosty Elk AB
 Author: Arne Sikstrom
"""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sessionstore import Session

from config import Config
from .frontend import frontend
from .nav import nav


def create_app():
    # We are using the "Application Factory"-pattern here, which is described
    # in detail inside the Flask docs:
    # http://flask.pocoo.org/docs/patterns/appfactories/

    app = Flask(__name__)

    app.config.from_object(Config)

    # Install our Bootstrap extension
    Bootstrap(app)

    Session(app)

    # Our application uses blueprints as well; these go well with the
    # application factory. We already imported the blueprint, now we just need
    # to register it:
    app.register_blueprint(frontend)

    # We initialize the navigation as well
    nav.init_app(app)

    return app
