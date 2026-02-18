from flask import Blueprint, make_response, jsonify

from chesser.service import board_service


board_bp = Blueprint('board', __name__, url_prefix='/board')


@board_bp.route('/fen/<gameId>', methods=['GET'])
def get_fen(gameId):
    return make_response(jsonify(board_service.get_fen_game(gameId)), 200)


@board_bp.route('/game/<id>', methods=['GET'])
def get_game_data(id):
    return make_response(jsonify(board_service.get_game_data(id)), 200)


@board_bp.route('/pieces', methods=['GET'])
def get_pieces():
    return make_response(jsonify(board_service.get_svg_piece_names()), 200)