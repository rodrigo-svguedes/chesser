from flask import Blueprint, make_response, jsonify, request

from chesser.service import board_service


board_bp = Blueprint('board', __name__, url_prefix='/board')


@board_bp.route('/pieces', methods=['GET'])
def get_pieces():
    return make_response(jsonify(board_service.get_svg_piece_names()), 200)


@board_bp.route('/pgn/analyse', methods=['POST'])
def get_fen_list_from_pgn():
    return make_response(jsonify(board_service.analyse_game(request.get_json()['pgn_code'])), 200)