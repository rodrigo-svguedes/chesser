import sys
import os
import re
import logging
import pickle
from contextlib import suppress

import pytest
from pytest_cases import fixture

from core import engine


logging.basicConfig(level=logging.INFO, format='%(levelname)s: $(message)s')
STOCKFISH_PATH = os.getenv('STOCKFISH_PATH')


@fixture(scope='session')
def cached_engine_analyse():
    """
        Using pickle module instead pytestconfig.cache, because the json module
        used by pytest can't serialize the engine analyse object
    """    
    root_path = os.getcwd()

    game_analyse_file_path = os.path.join(root_path, 'tests/data/pgn_data.pkl')
    pgn_games_file_path = os.path.join(root_path, 'tests/data/pgn_matches.pgn')

    data = []
    with suppress(FileNotFoundError, EOFError):
        with open(game_analyse_file_path, 'rb') as data_file:
            while True:
                logging.info('loading a new pgn analyse...')
                game_analyse = pickle.load(data_file)
                data.append(game_analyse)

    if not data:
        games_pgn = None
        with open(pgn_games_file_path, 'r') as pgn_file:
            games_pgn = re.split(r'(?=\[Event)', pgn_file.read())[1:]

        with open(game_analyse_file_path, 'wb') as game_file:
            eng = engine.Engine(STOCKFISH_PATH)
            for pgn in games_pgn:
                logging.info('saving a new pgn analyse...')
                game = eng.analyse(pgn)
                pickle.dump(game, game_file) 
                data.append(game)
            eng.quit_engine()

    return data


