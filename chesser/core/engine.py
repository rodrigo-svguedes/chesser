import io

import chess
import chess.pgn
import chess.engine

from core.models import GameData
from core.models import MoveAnalyse


class Engine:

    THREADS_THRESHOLD = 5
    DEFAULT_DEPTH = 15

    def __init__(self, stockfish_path):
        self.__engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.__engine.configure({"Threads": self.THREADS_THRESHOLD})    


    def quit_engine(self):
        self.__engine.quit()


    def analyse(self, pgn_code, depth=DEFAULT_DEPTH, multipv=1):
        game = chess.pgn.read_game(io.StringIO(pgn_code))
        board = game.board()
        
        game_data = GameData(game.headers['White'], game.headers['Black'], 
                             game.headers['WhiteElo'], game.headers['BlackElo'])
       
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

