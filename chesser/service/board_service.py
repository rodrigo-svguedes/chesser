import io
import math

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


def convert_stockfish_centipawns_to_bar_score(score, mate_threshold=10.0):
    
    if score.is_mate():
        mate_in = score.mate()
        if mate_in > 0:
            return 319.99 - (abs(mate_in) / 1000) * 0.1
        else:
            return -319.99 + (abs(mate_in) / 1000) * 0.1
    
    cp_score = score.score()
    
    max_score = mate_threshold
    
    if abs(cp_score) <= 500:
        converted = cp_score / 100.0
    else:
        sign = 1 if cp_score > 0 else -1
        abs_score = abs(cp_score)
        compressed = max_score * (1 - math.exp(-abs_score / 500))
        converted = sign * compressed
    
    return max(min(converted, max_score), -max_score)


def win_advantage(cp):
    cp = max(min(cp, 1000), -1000) 
    return 1 / (1 + math.exp(-0.004 * cp))


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
            'is_castling': board.is_castling(move)}

        if board.is_en_passant(move):
            analyse_data[index]['en_passant_move'] = True

        board.push(move)
        
        if move.promotion:
            piece_symbol = chess.piece_symbol(move.promotion)
            analyse_data[index]['promotion_to'] = piece_symbol.capitalize() if index % 2 == 0 else piece_symbol

        analyse_data[index]['fen'] = board.board_fen()
        #TODO: we still need to return the three best moves and their lines.
        info = engine.analyse(board, chess.engine.Limit(depth=10), multipv=3)

        score = info[0]['score'].white()
        evaluation = convert_stockfish_centipawns_to_bar_score(score)
        
        if not score.is_mate():
            prob = win_advantage(score.score())
            analyse_data[index]['win_advantage'] = f"{prob:.2f}"
        else:
            analyse_data[index]['mate_in'] = score.mate()
            if score.mate() < 0:
                analyse_data[index]['win_advantage'] = f"{0:.2f}"
            elif score.mate() > 0:
                analyse_data[index]['win_advantage'] = f"{1:.2f}"
            elif index % 2 == 0:
                analyse_data[index]['win_advantage'] = f"{1:.2f}"
            else:
                analyse_data[index]['win_advantage'] = f"{0:.2f}"

        analyse_data[index]['evaluation'] = f"{evaluation:.1f}"
    
    engine.quit()

    return [game_data, analyse_data]