import os

from flask import Blueprint, make_response, jsonify, request

from core.engine import Engine
from chesser.service import board_service
from chesser.service import analyse_service


board_bp = Blueprint('board', __name__, url_prefix='/board')


@board_bp.route('/pieces', methods=['GET'])
def get_pieces():
    return make_response(jsonify(board_service.get_svg_piece_names()), 200)


@board_bp.route('/pgn/analyse', methods=['POST'])
def get_fen_list_from_pgn():
    stockfish_path = os.getenv('STOCKFISH_PATH')
    if not stockfish_path:
        raise Exception('STOCKFISH_PATH must be setted!')
 
    polyglot_book_path = os.getenv('POLYGLOT_BOOK_PATH')
    if not polyglot_book_path:
        polyglot_book_path = f'{os.getcwd()}/assets/Performance.bin'

    engine = Engine(stockfish_path)
    engine_analyse = engine.analyse(request.get_json()['pgn_code'])
    response = analyse_service.classify_and_evaluate_moves(engine_analyse, polyglot_book_path)
    engine.quit_engine()

    return make_response(jsonify(response), 200)
