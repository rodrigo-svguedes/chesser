from flask import Flask
import click

from ext.database import db
from core.models import UserArchive, GamePGN


def create_db():
    """Creates database"""
    db.create_all()


def drop_db():
    """Cleans database"""
    db.drop_all()



def init_app(app: Flask):
    # add multiple commands in a bulk
    for command in [create_db, drop_db]:
        app.cli.add_command(app.cli.command()(command))

