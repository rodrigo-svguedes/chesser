from flask import Flask
from importlib import import_module
import tomllib

def load_extensions(app: Flask):
    for extension in app.config.get("EXTENSIONS"):
        # Split data in form `extension.path:factory_function`
        module_name, factory = extension.split(":")
        # Dynamically import extension module.
        ext = import_module(module_name)
        # Invoke factory passing app.
        getattr(ext, factory)(app)


def init_app(app: Flask):
    with open(r"settings.toml", "rb") as f:
        data = tomllib.load(f)
        app.config.update(data['default'])