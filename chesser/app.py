import sys, os
sys.path.append(os.path.dirname(__file__))

from flask import Flask

from api.api import init_app
from ext import configuration


def minimal_app():
    app = Flask(__name__)
    configuration.init_app(app)
    return app


def create_app():
    app = minimal_app()
    configuration.load_extensions(app)
    init_app(app)
    return app