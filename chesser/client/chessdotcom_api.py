import io
import datetime as dt
from datetime import date

import chess.pgn
import requests

from core.models import UserArchive, UserGamePGN


URL_BASE = 'https://api.chess.com/pub/player'


def get_player_months_archive(user_name):
    headers = {'user-agent': user_name}
    url = f'{URL_BASE}/{user_name}/games/archives'

    response = requests.get(url, headers=headers)
    archive_list = response.json().get('archives')
    
    archives = []
    for archive in archive_list:
        year, month = archive.split('/')[-2:]
        date_month = dt.date(int(year), int(month), 1)
        archives.append(UserArchive(user_name, date_month, archive))

    return archives


def get_games_from_archive(date_m: date, user_name):
    headers = {'user-agent': user_name}
    url = f'{URL_BASE}/{user_name}/games/{date_m.strftime("%Y/%m")}'
    res = requests.get(url, headers=headers)

    parse_format = '%Y.%m.%d %H:%M:%S'
    pgn_list = []
    for game in res.json().get('games'):
        pgn = game.get('pgn')
        game_h = chess.pgn.read_game(io.StringIO(pgn)).headers
        utcdate_str = f'{game_h.get("UTCDate")} {game_h.get("UTCTime")}'
        utcdate = dt.datetime.strptime(utcdate_str, parse_format)
        pgn_list.append(UserGamePGN(user_name, utcdate, pgn))

    return pgn_list 
