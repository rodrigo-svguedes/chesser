import sys, os
sys.path.append(os.path.dirname(__file__))

from flask import Flask

from core import load


def minimal_app():
    app = Flask(__name__)
    return app


def create_app():
    app = minimal_app()
    load.load_extensions(app)
    return app
