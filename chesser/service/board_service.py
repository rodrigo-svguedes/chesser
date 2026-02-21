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


def analyse_game(pgn_code):

    stockfish_path = "/home/rodrigo/Downloads/stockfish/stockfish-ubuntu-x86-64-avx2"
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    game = chess.pgn.read_game(io.StringIO(pgn_code))
    
    board = game.board()

    game_data = {
        'black_player': f"{game.headers['Black']} - {game.headers['BlackElo']}",
        'white_player': f"{game.headers['White']} - {game.headers['WhiteElo']}"
    }

    def centipawns_to_bar(cp):
        cp = max(min(cp, 1000), -1000) 
        return 1 / (1 + math.exp(-0.004 * cp))

    analyse_data = {}

    for index, move in enumerate(game.mainline_moves()):
        
        analyse_data[index] = {
            'move': move.uci(), 
            'engine_moves': {},
            'from_square': move.from_square,
            'to_square': move.to_square,
            'is_castling': board.is_castling(move)}

        board.push(move)
        
        if move.promotion:
            piece_symbol = chess.piece_symbol(move.promotion)
            analyse_data[index]['promotion_to'] = piece_symbol.capitalize() if index % 2 == 0 else piece_symbol

        analyse_data[index]['fen'] = board.board_fen()
        info = engine.analyse(board, chess.engine.Limit(depth=10), multipv=3)

        for i, entry in enumerate(info):
            score = entry["score"].white()
            if score.is_mate():
                analyse_data[index]['is_mate'] = True
                analyse_data[index]['mate_in'] = score.mate()
                if score.mate() > 0:
                    analyse_data[index]['mate_for'] = 'white'
                    analyse_data[index]['evaluation'] = "10"
                    analyse_data[index]['win_advantage'] = "1"
                elif score.mate() < 0:
                    analyse_data[index]['mate_for'] = 'black'
                    analyse_data[index]['evaluation'] = "-10"
                    analyse_data[index]['win_advantage'] = "0"
                else:
                    analyse_data[index]['mated'] = True
                break
            else:
                cp = score.score()
                prob = centipawns_to_bar(cp)
                analyse_data[index]['score'] = score.score()           
                analyse_data[index]['engine_moves'][i] = entry["pv"][0].uci()
                analyse_data[index]['evaluation'] = f"{cp * 0.004:.2f}"
                analyse_data[index]['win_advantage'] = f"{prob:.2f}"

    engine.quit()

    return [game_data, analyse_data]