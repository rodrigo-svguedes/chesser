import os
import logging
from collections import defaultdict

import chess
import chess.engine
from pytest_cases import fixture, parametrize

from core.engine import MoveAnalyse
from service.analyse_service import win_advantage, game_accuracy_from_cps, classify_and_evaluate_moves


logging.basicConfig(level=logging.INFO, format='%(levelname)s: $(message)s')
POLYGLOT_BOOK_PATH = f'{os.getcwd()}/assets/Performance.bin'


def create_score(cp):
    return chess.engine.PovScore(chess.engine.Cp(cp), chess.WHITE).white()

def create_move(score):
    return MoveAnalyse(None, None, None, None, None, None, None, win_advantage=win_advantage(score))

def is_close_to(value, expected, tolerance):
    return abs(value - expected) <= tolerance


def test_assert_test():
    win_adv = round(win_advantage(create_score(1000)), 2)
    logging.info(f'win%: {win_adv}')
    assert is_close_to(win_adv, 97, 2)


def test_game_accuracy_from_cps():
    """
    Once we have rewrite the lichess game accuracy function, we also have
    to do the same tests.
    """
    WHITE, BLACK = 0, 1
    cp = lambda cp: create_move(create_score(cp))
    is_close_to = lambda v, e, t: abs(v - e) <= t
    # two good moves
    acc = game_accuracy_from_cps([cp(15), cp(15)])
    assert is_close_to(acc[WHITE], 100, 1)
    assert is_close_to(acc[BLACK], 100, 1)
    # white blunders on first move
    acc = game_accuracy_from_cps([cp(-900), cp(-900)])
    assert is_close_to(acc[WHITE], 10, 5)
    assert is_close_to(acc[BLACK], 100, 1)
    # black blunders on first move
    acc = game_accuracy_from_cps([cp(15), cp(900)])
    assert is_close_to(acc[WHITE], 100, 1)
    assert is_close_to(acc[BLACK], 10, 5)
    # both blunders on first move
    acc = game_accuracy_from_cps([cp(-900), cp(0)])
    assert is_close_to(acc[WHITE], 10, 5)
    assert is_close_to(acc[BLACK], 10, 5)
    # 20 perfect moves
    acc = game_accuracy_from_cps([cp(15)] * 20)
    assert is_close_to(acc[WHITE], 100, 1)
    assert is_close_to(acc[BLACK], 100, 1)
    # 20 perfect moves and a white blunder
    acc = game_accuracy_from_cps([cp(15)] * 20 + [cp(-900)])
    assert is_close_to(acc[WHITE], 50, 5)
    assert is_close_to(acc[BLACK], 100, 1)
    # 21 perfect moves and a black blunder
    acc = game_accuracy_from_cps([cp(15)] * 21 + [cp(900)])
    assert is_close_to(acc[WHITE], 100, 1)
    assert is_close_to(acc[BLACK], 50, 5)
    # 5 average moves (65 cpl) on each side
    acc = game_accuracy_from_cps([cp(-50), cp(15)] * 5)
    assert is_close_to(acc[WHITE], 76, 8)
    assert is_close_to(acc[BLACK], 76, 8)
    # 50 average moves (65 cpl) on each side
    acc = game_accuracy_from_cps([cp(-50), cp(15)] * 50)
    assert is_close_to(acc[WHITE], 76, 8)
    assert is_close_to(acc[BLACK], 76, 8)
    # 50 mediocre moves (150 cpl) on each side
    acc = game_accuracy_from_cps([cp(-135), cp(15)] * 50)
    assert is_close_to(acc[WHITE], 54, 8)
    assert is_close_to(acc[BLACK], 54, 8)
    # 50 terrible moves (500 cpl) on each side
    acc = game_accuracy_from_cps([cp(-435), cp(15)] * 50)
    assert is_close_to(acc[WHITE], 20, 8)
    assert is_close_to(acc[BLACK], 20, 8)


def test_classify_and_evaluate_moves(cached_engine_analyse):
    """
    This is a analysis simulation for DEPTH 15
    """    
    game_data = classify_and_evaluate_moves(cached_engine_analyse[0], POLYGLOT_BOOK_PATH)
    moves = game_data.move_analyse_list

    accuracies = (53.22, 55.14, 55.23, 55.59, 55.77, 56.95, 57.13, 57.22, 56.86, 56.50, 
                  53.31, 53.58, 53.86, 54.77, 55.05, 54.77, 53.77, 53.13, 52.85, 54.22, 
                  53.31, 53.31, 53.13, 55.50, 53.22, 55.59, 52.85, 53.31, 53.86, 54.04, 
                  54.22, 53.58, 50.64, 53.31, 49.82, 47.24, 47.06, 46.60, 46.60, 46.78, 
                  45.41, 44.32, 45.87, 45.78, 45.23, 45.59, 46.05, 56.14, 56.05, 56.50, 
                  56.14, 56.14, 56.05, 56.23, 56.50, 55.86, 57.49, 57.40, 55.50, 54.13, 
                  54.32, 68.74, 68.58, 68.74, 70.30, 70.38, 70.22, 69.99, 69.68, 69.60, 
                  70.83, 72.26, 71.59, 72.19, 72.85, 72.04, 72.41, 72.41, 73.06, 76.33, 
                  78.77, 81.29, 74.77, 79.85, 81.40, 80.26, 79.85)

    for i, (p, n) in enumerate(zip(moves[::2], moves[1::2])):
        #logging.info(f'{i:0>2}. {p.move}: {round(p.win_advantage, 2):0<5} - {n.move}: {round(n.win_advantage, 2):0<5}')
        assert round(p.win_advantage, 2) == accuracies[i*2]
        assert round(n.win_advantage, 2) == accuracies[(i*2)+1]


@parametrize('index, white, black', [(0, 97, 94), (1, 93, 98), (2, 74, 75), (3, 82, 65), (4, 89, 84), (5, 75, 88)])
def test_game_accuracies(cached_engine_analyse, index, white, black):
    # checks some games accuracies at DEPTH 15
    game_data = classify_and_evaluate_moves(cached_engine_analyse[index], POLYGLOT_BOOK_PATH)

    logging.info(f'white_acc: {game_data.white_accuracy} - black_acc: {game_data.black_accuracy}')
    assert is_close_to(game_data.white_accuracy, white, 3)
    assert is_close_to(game_data.black_accuracy, black, 3)


@parametrize('index, expected_move_count', [
    (0, {'book': (6, 8), 'good': (5, 4), 'best': (26, 25), 'excellent': (6, 3), 'inaccuracy': (1, 1), 'mistake': (0, 2)}),
    (1, {'book': (9, 9), 'good': (3, 3), 'best': (16, 23), 'excellent': (6, 5), 'inaccuracy': (6, 0)})
])
def test_game_classification(cached_engine_analyse, index, expected_move_count):
    # checks some games move classification counts 
    game_data = classify_and_evaluate_moves(cached_engine_analyse[index], POLYGLOT_BOOK_PATH)

    move_class_count = {0: defaultdict(int), 1: defaultdict(int)}
    for index, move in enumerate(game_data.move_analyse_list):
        move_class_count[index % 2][move.move_class] += 1

    for key in move_class_count.keys():
        for move_class, value in move_class_count[key].items():
            logging.info(f'{key} -> {move_class}: {value}')
            assert value == expected_move_count[move_class][key]

