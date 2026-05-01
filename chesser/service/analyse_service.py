import os
import math
import statistics
import itertools as it

from decimal import Decimal, ROUND_DOWN
from contextlib import suppress
from dataclasses import replace

import chess
import chess.pgn
import chess.engine
import chess.polyglot


MATE_THRESHOLD = 10
CP_CEILING = 1000


def win_advantage(score):
    """
        That's lichess function to get the 
        winning chance of a position based 
        on stockfish's centpawns score
    """
    if score.is_mate():
        return 100 if score.mate() >= 0 else 0
    
    win_adv = 2 / (1 + math.exp(-0.00368208 * score.score())) - 1
    win_adv = max(min(1, win_adv), -1)

    return 50 + 50 * max(min(win_adv, CP_CEILING), -CP_CEILING)


def score_to_evalbar_points(score, win_adv):
    """
        A function to normalize the centpawns score
        provided by the stockfish.
    """
    return MATE_THRESHOLD if score.is_mate() else (win_adv - 50) / 5


def accuracy_from_win_percents(before, after):
    """
        That's lichess function to get the accuracy of a move
    """
    if after >= before: 
        return 100

    winDiff = before - after
    raw = 103.1668100711649 * math.exp(-0.04354415386753951 * winDiff) - 3.166924740191411
    raw += 1 # uncertainty bonus (due to imperfect analysis)
    return min(max(raw, 0), 100)


def game_accuracy_from_cps(move_analyse_list):
    all_win_percents = [move.win_advantage for move in move_analyse_list]
    window_size = min(max(len(move_analyse_list) // 10, 2), 8)
    
    sliding_windows = [
        all_win_percents[i : i + window_size]
        for i in range(len(all_win_percents) - window_size + 1)
    ]

    fill_count = min(window_size, len(all_win_percents)) - 2
    initial_padding = all_win_percents[:window_size] * fill_count 

    windows = initial_padding + sliding_windows

    weights = [] 
    for window in windows:
        weight = 0.0
        with suppress(statistics.StatisticsError, TypeError):
            weight = statistics.stdev(window)
        weights.append(min(max(weight, 0.5), 12))
    
    
    weighted_accuracies = []
    for index, ((prev_win, next_win), weight) in enumerate(zip(it.pairwise(all_win_percents), weights)):
        is_white = index % 2 == 0 
        first, second = (prev_win, next_win) if not is_white else (next_win, prev_win)
        accuracy = accuracy_from_win_percents(first, second)
        #print(f'if_white: {is_white} | first: {first} - second: {second} | accuracy: {accuracy}')
        weighted_accuracies.append([(accuracy, weight), is_white])

    #print(f'weights_size: {len(weights)}')
    #print(f'sliding_size: {len(sliding_windows)}')
    #print(f'initial_size: {len(initial_padding)}')
    #print(f'windows_size: {len(windows)}')
    #print(f'all_win_percents_size: {len(all_win_percents)}')
    #print('='*40)
    #print(weighted_accuracies)

    white_weighted_accuracies = [acc[0][0] for acc in weighted_accuracies if acc[1]]
    white_weights = [acc[0][1] for acc in weighted_accuracies if acc[1]]
    black_weighted_accuracies = [acc[0][0] for acc in weighted_accuracies if not acc[1]]
    black_weights = [acc[0][1] for acc in weighted_accuracies if not acc[1]]

    white_weighted_mean = statistics.fmean(white_weighted_accuracies, white_weights)
    white_harmonic_mean = statistics.harmonic_mean(white_weighted_accuracies) 

    black_weighted_mean = statistics.fmean(black_weighted_accuracies, black_weights)
    black_harmonic_mean = statistics.harmonic_mean(black_weighted_accuracies) 

    white_accuracy = round((white_weighted_mean + white_harmonic_mean) / 2, 2)
    black_accuracy = round((black_weighted_mean + black_harmonic_mean) / 2, 2)

    return (white_accuracy, black_accuracy) 
    

def classify_move(is_white_move, index, move_analyse_list):
    """
    Classify a move according to chess.com's classification system.
    Uses expected points model based on win advantage changes.
    """
    move_analyse = move_analyse_list[index]
    previous_move_analyse = move_analyse_list[index-1]

    current_win_adv = move_analyse.win_advantage
    previous_win_adv = previous_move_analyse.win_advantage 
    
    previous_ep = previous_win_adv / 100
    current_ep = current_win_adv / 100
    
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

        move_analyse.win_advantage = win_advantage(score)
        move_analyse.evaluation = score_to_evalbar_points(score, move_analyse.win_advantage)
        board.push(chess.Move.from_uci(move_analyse.move))

        if book.get(board):
            move_analyse.move_class = 'book'
        elif index > 0:
            move_analyse.move_class = classify_move(is_white_turn, index, move_analyse_list)

    white_acc, black_acc = game_accuracy_from_cps(move_analyse_list)
    game_data = replace(game_data, 
                        white_accuracy=white_acc, 
                        black_accuracy=black_acc)

    game_data.move_analyse_list = move_analyse_list
    return game_data

