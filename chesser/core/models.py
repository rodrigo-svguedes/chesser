from typing import List
from datetime import datetime, date

from sqlalchemy import Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ext.database import db


class UserArchive(db.Model):
    __tablename__ = 'user_archive'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String)
    date_month: Mapped[date] = mapped_column(Date)
    pgn_games: Mapped[List['GamePGN']] = relationship()
    

class GamePGN(db.Model):
    __tablename__ = 'game_pgn'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_arch_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_archive.id'))
    register: Mapped[datetime] = mapped_column(DateTime)
    pgn: Mapped[str] = mapped_column(String)

