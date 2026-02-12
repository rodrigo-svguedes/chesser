from flask import render_template, Blueprint

view_bp = Blueprint('view', __name__, url_prefix='', template_folder='templates')


class Board:
    def __init__(self):
        self.initial_pos = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.pieces = ['rook-b', 'knight-b', 'bishop-b', 'queen-b', 'king-b', 'bishop-b', 'knight-b', 'rook-b',
                       'pawn-b', 'pawn-b', 'pawn-b', 'pawn-b', 'pawn-b', 'pawn-b', 'pawn-b', 'pawn-b',
                       '', '', '', '', '', '', '', '',
                       '', '', '', '', '', '', '', '',
                       '', '', '', '', '', '', '', '',
                       '', '', '', '', '', '', '', '',
                       'PAWN-W', 'PAWN-W', 'PAWN-W', 'PAWN-W', 'PAWN-W', 'PAWN-W', 'PAWN-W', 'PAWN-W',
                       'ROOK-W', 'KNIGHT-W', 'BISHOP-W', 'QUEEN-W', 'KING-W', 'BISHOP-W', 'KNIGHT-W', 'ROOK-W']
        
    def piece_at(self, position):
        return self.pieces[position] if 0 <= position < len(self.pieces) else None


@view_bp.route('/board', methods=['GET'])
def index():
    board = Board()
    return render_template("board.html", board=board)