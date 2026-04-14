import os
import tomllib

from flask import Flask


def load_env_var(env_varnames: list[tuple]):
    envs = {}
    for (env, default_value) in env_varnames:
        value = os.getenv(env)
        if not default_value and not value:
            raise Exception(f'THE ENVIRONMENT VARIABLE MUST BE SETTLED: {env}.')
        envs[env] = value or default_value
    return envs
        

def init_app(app: Flask):
    with open(r"settings.toml", "rb") as f:
        data = tomllib.load(f)
        app.config.update(data['default'])

    env_vars = [('STOCKFISH_PATH', None), 
                ('POLYGLOT_BOOK_PATH', f'{os.getcwd()}/assets/Performance.bin')]

    envs = load_env_var(env_vars)
    app.config.update(envs)
