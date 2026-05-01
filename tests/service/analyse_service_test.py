import os
import logging

import chess
import chess.engine

from service import analyse_service

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: $(message)s'
)

POLYGLOT_BOOK_PATH = f'{os.getcwd()}/assets/Performance.bin'

def __generate_basic_board():
    board = chess.Board()
    return board

def __move(move):
    return chess.Move.from_uci(move)
    

def test_assert_test():
    score = chess.engine.PovScore(chess.engine.Cp(1000), chess.WHITE).white()
    win_adv = round(analyse_service.win_advantage(score), 2)
    
    logging.info(f'win%: {win_adv}')
     
    assert win_adv == 97.54


def test_classify_and_evaluate_moves(cached_engine_analyse):
    game_data = analyse_service.classify_and_evaluate_moves(cached_engine_analyse, POLYGLOT_BOOK_PATH)
    logging.info(f'white_acc: {game_data.white_accuracy} - black_acc: {game_data.black_accuracy}')
    for index, move in enumerate(game_data.move_analyse_list):
        is_white_turn = index % 2 == 0
        #logging.info(f'{"white" if is_white_turn else "black"} - {move.move}: {round(move.win_advantage, 2)}')
