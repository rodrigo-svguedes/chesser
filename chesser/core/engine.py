import io

import chess
import chess.pgn
import chess.engine

from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal


@dataclass
class GameData:
    white_player: str
    black_player: str 
    white_elo: int
    black_elo: int
    white_accuracy: float
    black_accuracy: float
    move_analyse_list: list = field(default_factory=list)


@dataclass
class MoveAnalyse:
    move: str
    from_square: int
    to_square: int
    promotion_to: str
    is_check: bool
    is_castling: bool
    is_en_passant: bool
    fen: Optional[str] = None
    mate_in: Optional[int] = None
    best_move: Optional[str] = None
    move_class: Optional[str] = None
    win_advantage: Optional[Decimal] = None
    evaluation: Optional[Decimal] = None
    engine_moves: dict = field(default_factory=dict)


class Engine:

    THREADS_THRESHOLD = 1
    DEFAULT_DEPTH = 15

    def __init__(self, stockfish_path):
        self.__engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.__engine.configure({"Threads": self.THREADS_THRESHOLD})    


    def quit_engine(self):
        self.__engine.quit()


    def analyse(self, pgn_code, depth=DEFAULT_DEPTH, multipv=1):
        game = chess.pgn.read_game(io.StringIO(pgn_code))
        board = game.board()
        
        game_data = GameData(game.headers.get('White'), game.headers.get('Black'), 
                             game.headers.get('WhiteElo'), game.headers.get('BlackElo'), 
                             None, None)
       
        analyse_move_list = []

        is_promotion = lambda move: chess.piece_symbol(move.promotion) if move.promotion else None
        for index, move in enumerate(game.mainline_moves()):
            is_white_turn = index % 2 == 0

            piece_promotion = is_promotion(move)
            if piece_promotion and is_white_turn:
                piece_promotion = piece_promotion.capitalize()
 
            move_analyse = MoveAnalyse(
                move.uci(), 
                move.from_square, 
                move.to_square, 
                piece_promotion,
                board.gives_check(move),
                board.is_castling(move),
                board.is_en_passant(move))

            board.push(move)
            info = self.__engine.analyse(board, chess.engine.Limit(depth=depth), multipv=multipv)
            move_analyse.fen = board.board_fen()

            if info[0].get('pv'):
                move_analyse.best_move = info[0].get('pv')[0].uci()

            score = info[0]['score'].white()

            if score.is_mate():
                move_analyse.mate_in = score.mate()
            
            analyse_move_list.append([info, move_analyse])
    
        game_data.move_analyse_list = analyse_move_list

        return game_data

