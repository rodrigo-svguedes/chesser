from sqlalchemy import select, and_

from ext.database import db
from core.models import UserArchive as user
from core.models import GamePGN as game

from core.models import UserArchive


def persist_user_archives(user_archive: list[user]):
    db.session.add_all(user_archive)
    db.session.flush()
    db.session.commit()
    

def persist_games_pgn(games_pgn: list[game]):
    db.session.add_all(games_pgn)
    db.session.flush()
    db.session.commit()
    

def select_archive_by_username_and_month(user_name, date_game):
    slc = select(user).where(and_(user.user_name.like(user_name), user.date_month == date_game))
    return db.session.execute(slc).first()


def select_archives_by_username(user_name):
    slc = select(UserArchive).where(UserArchive.user_name.like(user_name))
    return db.session.execute(slc).all()


def select_games_by_username_and_month(user_name, date_game):
    slc = select(game).join(user).where(user.user_name.like(user_name))
    return db.session.execute(slc).all()
