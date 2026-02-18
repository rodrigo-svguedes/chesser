import io

from collections import namedtuple

import chess
import chess.pgn


Board = namedtuple('Board', 'ranks, files')

def get_board_coordinates():
    ranks = {0: '8', 8: '7', 16: '6', 24: '5', 32: '4', 40: '3', 48: '2', 56: '1'}
    files = {56: 'a', 57: 'b', 58: 'c', 59: 'd', 60: 'e', 61: 'f', 62: 'g', 63: 'h'}
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

pgn_code = '''
    [Event "Live Chess"]
    [Site "Chess.com"]
    [Date "2026.02.16"]
    [Round "?"]
    [White "RandomGuy"]
    [Black "R0drigoGuedes"]
    [Result "0-1"]
    [TimeControl "180"]
    [WhiteElo "1398"]
    [BlackElo "1394"]
    [Termination "R0drigoGuedes venceu por desistência"]
    [ECO "A40"]
    [EndTime "16:33:58 GMT+0000"]
    [Link "https://www.chess.com/game/live/164778245142?move=0"]

    1. d4 e6 2. Bf4 d5 3. e3 c5 4. Nf3 Nf6 5. c3 cxd4 6. exd4 Bd6 7. Bg3 O-O 8. Bd3
    Nc6 9. Nbd2 b6 10. Qc2 Bb7 11. b4 Ne7 12. Ne5 Ng6 13. a4 Bxe5 14. dxe5 Nd7 15.
    Nf3 Qc7 16. O-O Rac8 17. Rac1 Qc6 18. b5 Qc7 19. Rfe1 Nc5 20. Bf1 Qd7 21. Nd4
    Rc7 22. f4 Ne4 23. Rxe4 dxe4 24. Qxe4 Bxe4 0-1'''.replace(4*' ', '')
    
#TODO: this function must take from a database or from chess.com
def get_fen_game(game_id):
    
    game = chess.pgn.read_game(io.StringIO(pgn_code))
    
    board = game.board()
    fen_list = {}

    for index, move in enumerate(game.mainline_moves()):
        board.push(move)
        fen_list[index] = board.board_fen()

    return fen_list


def get_game_data(game_id):
    game = chess.pgn.read_game(io.StringIO(pgn_code))
    game_data = {
        'black_player': game.headers['Black'],
        'white_player': game.headers['White']
    }
    return game_data