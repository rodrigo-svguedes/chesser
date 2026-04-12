import tomllib

from flask import Flask


def init_app(app: Flask):
    with open(r"settings.toml", "rb") as f:
        data = tomllib.load(f)
        app.config.update(data['default'])
