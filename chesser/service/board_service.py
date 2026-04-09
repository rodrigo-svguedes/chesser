from collections import namedtuple


def get_board_coordinates():
    Board = namedtuple('Board', 'ranks, files')
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

