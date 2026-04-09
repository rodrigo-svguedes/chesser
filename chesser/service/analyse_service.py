import io
import os
import math
from decimal import Decimal, ROUND_DOWN

import chess
import chess.pgn
import chess.engine
import chess.polyglot

from core.models import GameData
from core.models import MoveAnalyse


MATE_THRESHOLD = 10
DECIMAL_ONE_HUNDRED = Decimal('100')
DECIMAL_ZERO = Decimal('0')


def win_advantage(score):
    """
        That's lichess function to get the 
        winning chance of a position based 
        on stockfish's centpawns score
    """
    if score.is_mate():
        return DECIMAL_ONE_HUNDRED if score.mate() >= 0 else DECIMAL_ZERO
    
    win_adv = Decimal(2 / (1 + math.exp(-0.00368208 * score.score())) - 1)
    win_adv = min(1, win_adv) or max(-1, win_adv)
    return Decimal(50 + 50 * win_adv)


def score_to_evalbar_points(score, win_adv):
    """
        A function to normalize the centpawns score
        provided by the stockfish.
    """
    return Decimal(MATE_THRESHOLD) if score.is_mate() else Decimal((win_adv - 50) / 5)


def accuracy_from_win_percents(before: Decimal, after: Decimal):
    """
        That's lichess function to get the accuracy of a move
    """
    if after >= before: 
        return DECIMAL_ONE_HUNDRED
    else:
        winDiff = before - after
        raw = 103.1668 * math.exp(-0.04354 * winDiff) + -3.1669
        raw + 1 # uncertainty bonus (due to imperfect analysis)
        if raw > 100: return DECIMAL_ONE_HUNDRED
        if raw < 0: return DECIMAL_ZERO 


def classify_move(is_white_move, index, move_analyse_list):
    """
    Classify a move according to chess.com's classification system.
    Uses expected points model based on win advantage changes.
    """
    move_analyse = move_analyse_list[index]
    previous_move_analyse = move_analyse_list[index-1]

    current_win_adv = move_analyse.win_advantage
    previous_win_adv = previous_move_analyse.win_advantage 
    
    previous_ep = previous_win_adv / DECIMAL_ONE_HUNDRED
    current_ep = current_win_adv / DECIMAL_ONE_HUNDRED
    
    # Calculate expected points lost
    points_lost = Decimal(abs(current_ep - previous_ep)).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

    #print(f'{analyse_data[previous_index+1]["move"]}: {current_ep}, {previous_ep} => points_lost: {points_lost}.')
    #print('='*25)
    
    missed_class = ['inaccuracy', 'miss', 'mistake', 'blunder']
    if points_lost >= Decimal('0.05') \
        and current_ep <= Decimal('0.7') \
        and previous_ep >= Decimal('0.3') \
        and previous_move_analyse.move_class in missed_class:
        return 'miss'

    best_move = previous_move_analyse.best_move

    # Classify based on expected points thresholds
    if best_move == move_analyse.move:
        return "best"
    elif points_lost < Decimal('0.02'):
        return "excellent"
    elif points_lost < Decimal('0.05'):
        return "good"
    elif points_lost < Decimal('0.1'):
        return "inaccuracy"
    elif points_lost < Decimal('0.2'):
        return "mistake"
    else:
        return "blunder"


def classify_and_evaluate_moves(game_data, polyglot_book_path):

    move_analyse_list = [move[1] for move in game_data.move_analyse_list]
    book = chess.polyglot.open_reader(polyglot_book_path)
    board = chess.Board()

    for index, (info, move_analyse) in enumerate(game_data.move_analyse_list):
        is_white_turn = index % 2 == 0
        score = info[0]['score'].white()

        win_adv = win_advantage(score)

        move_analyse.win_advantage = Decimal(win_adv)
        move_analyse.evaluation = score_to_evalbar_points(score, win_adv)

        board.push(chess.Move.from_uci(move_analyse.move))

        if book.get(board):
            move_analyse.move_class = 'book'
        elif index > 0:
            move_analyse.move_class = classify_move(is_white_turn, index, move_analyse_list)

    game_data.move_analyse_list = move_analyse_list
    return [game_data, move_analyse_list]
