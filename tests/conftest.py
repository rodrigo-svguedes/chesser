import os
import logging
import pickle
from contextlib import suppress

import pytest
from pytest_cases import fixture

from core import engine


pgn_code = """
    [Event "Live Chess"]
    [Site "Chess.com"]
    [Date "2026.03.21"]
    [Round "?"]
    [White "R0drigoGuedes"]
    [Black "PlayChessNowOrNever"]
    [Result "1-0"]
    [TimeControl "180"]
    [WhiteElo "1327"]
    [BlackElo "1330"]
    [Termination "R0drigoGuedes venceu por xeque-mate"]
    [ECO "C00"]
    [EndTime "1:29:21 GMT+0000"]
    [Link "https://www.chess.com/game/live/166220451820?move=0"]

    1. e4 e6 2. Nf3 b6 3. d4 Bb7 4. Nc3 Bb4 5. Bd3 Nf6 6. Qe2 h6 7. e5 Nd5 8. Bd2
    Bxc3 9. bxc3 Qe7 10. c4 Nb4 11. Be4 N8c6 12. O-O O-O-O 13. a3 Na6 14. d5 exd5
    15. cxd5 Ncb8 16. c4 d6 17. exd6 Qxd6 18. Bf5+ Nd7 19. Nd4 g6 20. Nb5 Qf6 21.
    Bxd7+ Rxd7 22. Bc3 Qd8 23. Bxh8 Qxh8 24. Rfe1 Qg7 25. Qe8+ Rd8 26. Nxa7+ Kb8 27.
    Nc6+ Bxc6 28. Qxd8+ Kb7 29. dxc6+ Kxc6 30. Qd5# 1-0
"""


def engine_analyse():
    stockfish_path = os.getenv('STOCKFISH_PATH')

    eng = engine.Engine(stockfish_path)
    engine_analyse = eng.analyse(pgn_code.replace(' '*4, ''))
    eng.quit_engine()

    return engine_analyse


@fixture(scope='session')
def cached_engine_analyse():
    """
        Using pickle module instead pytestconfig.cache, because the json module
        used by pytest can't serialize the engine analyse object
    """    
    data = None
    with suppress(FileNotFoundError):
        with open(os.path.join(os.getcwd(), 'data.pkl'), 'rb') as data_file:
            data = pickle.load(data_file) 

    if not data:
        data = engine_analyse()
        with open(os.path.join(os.getcwd(), 'data.pkl'), 'wb') as data_file:
            pickle.dump(data, data_file) 

    return data


