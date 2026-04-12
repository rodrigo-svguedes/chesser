import os
from os.path import dirname, join
from importlib import import_module
from contextlib import suppress


def load_extensions(app):
    modules = {'api.rest', 'api.view', 'ext'}
    project_path = dirname(dirname(__file__))
    for module in modules:
        path = join(project_path, module.replace('.', '/'))
        files = [file[:-3] for file in os.listdir(path) if file[-3:] == '.py']
        for file in files:
            # Dynamically import extension module.
            ext = import_module(f'{module}.{file}')
            with suppress(AttributeError):
                _init_app = getattr(ext, 'init_app')
                if not _init_app: continue
                _init_app(app)
 
