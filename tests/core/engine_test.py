import logging
import pytest

logging.basicConfig(level=logging.INFO, format='%(levelname)s: $(message)s')

def test_engine_analyse(cached_engine_analyse):
    game_data = cached_engine_analyse
    #move_analyse = game_data.move_analyse_list[10][1]
    '''assert game_data.white_player == 'R0drigoGuedes'
    assert game_data.black_player == 'PlayChessNowOrNever'
    assert game_data.white_elo == '1327'
    assert game_data.black_elo == '1330'
    assert move_analyse.move == 'd1e2'
    '''
