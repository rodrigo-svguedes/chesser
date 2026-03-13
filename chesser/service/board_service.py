import io
import math
from decimal import Decimal
from collections import namedtuple

import chess
import chess.pgn
import chess.engine

Board = namedtuple('Board', 'ranks, files')
def get_board_coordinates():
    ranks = {0: '1', 8: '2', 16: '3', 24: '4', 32: '5', 40: '6', 48: '7', 56: '8'}
    files = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    return Board(ranks, files)


def get_svg_piece_names():
    return {
        'r': 'rook-b',
        'b': 'bishop-b',
        'n': 'knight-b',
        'q': 'queen-b',
        'k': 'king-b',
        'p': 'pawn-b',
        'R': 'rook-w',
        'B': 'bishop-w',
        'N': 'knight-w',
        'Q': 'queen-w',
        'K': 'king-w',
        'P': 'pawn-w',
    }

def win_advantage(score):
    """
        That's lichess function to get the 
        winning chance of a position based 
        on stockfish's centpawns score
    """
    if score.is_mate():
        return 100 if score.mate() > 0 else 0
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * score.score())) - 1)


MATE_THRESHOLD = 10
def score_to_evalbar_points(score, win_adv):
    """
        A function to normalize the centpawns score
        provided by the stockfish.
    """
    return MATE_THRESHOLD if score.is_mate() else (win_adv - 50) / 5


def accuracy_from_win_percents(before: Decimal, after: Decimal):
    """
        That's lichess function to get the accuracy of a move
    """
    if after >= before: 
        return 100
    else:
        winDiff = before - after
        raw = 103.1668100711649 * math.exp(-0.04354415386753951 * winDiff) + -3.166924740191411
        raw + 1 # uncertainty bonus (due to imperfect analysis)
        if raw > 100: return 100
        if raw < 0: return 0


def classify_move(previous_win_adv, win_adv):
    """
        A function to classify the move according to chess.com
        TODO: Still need to implement all the logic
    """
    win_diff = abs(win_adv/100 - previous_win_adv/100)
    
    if win_diff <= 0.01:
        return "best"
    elif win_diff <= 0.02:
        return "excellent"
    elif win_diff <= 0.05:
        return "good"
    elif win_diff <= 0.1:
        return "inaccuracy"
    elif win_diff <= 0.2:
        return "mistake"
    
    return "blunder"


def analyse_game(stockfish_path, pgn_code):

    #TODO: We need a pool of stockfish's instances
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    
    game = chess.pgn.read_game(io.StringIO(pgn_code))
    board = game.board()

    game_data = {
        'black_player': f"{game.headers['Black']} - {game.headers['BlackElo']}",
        'white_player': f"{game.headers['White']} - {game.headers['WhiteElo']}"
    }

    analyse_data = {}

    for index, move in enumerate(game.mainline_moves()):
        
        analyse_data[index] = {
            'move': move.uci(), 
            'engine_moves': {},
            'from_square': move.from_square,
            'to_square': move.to_square,
            'is_check': board.gives_check(move),
            'is_castling': board.is_castling(move),
            'en_passant_move': board.is_en_passant(move)}
        
        board.push(move)
        
        if move.promotion:
            piece_symbol = chess.piece_symbol(move.promotion)
            analyse_data[index]['promotion_to'] = piece_symbol.capitalize() if index % 2 == 0 else piece_symbol

        analyse_data[index]['fen'] = board.board_fen()
        #TODO: we still need to return the three best moves and their lines.
        info = engine.analyse(board, chess.engine.Limit(depth=10), multipv=3)

        score = info[0]['score'].white()
        prob = win_advantage(score)
        evaluation = score_to_evalbar_points(score, prob)

        analyse_data[index]['win_advantage'] = f"{prob:.2f}"
        if score.is_mate():
            analyse_data[index]['mate_in'] = score.mate()
        
        if index > 1:
            move_class = classify_move(float(analyse_data[index-2]['win_advantage']), prob)
            analyse_data[index]['move_class'] = move_class

        analyse_data[index]['evaluation'] = f"{evaluation:.1f}"
    
    engine.quit()

    return [game_data, analyse_data]
