import datetime as dt

from flask import Blueprint, make_response, jsonify, request, current_app

from core.engine import Engine
from chesser.service import board_service
from chesser.service import analyse_service
from chesser.service import chessdotcom_service


board_bp = Blueprint('board', __name__, url_prefix='/board')
def init_app(app): app.register_blueprint(board_bp)


@board_bp.route('/pieces', methods=['GET'])
def get_pieces():
    return make_response(jsonify(board_service.get_svg_piece_names()), 200)


@board_bp.route('/pgn/analyse', methods=['POST'])
def analyse_game_from_pgn():
    stockfish_path = current_app.config.get('STOCKFISH_PATH')
    polyglot_book_path = current_app.config.get('POLYGLOT_BOOK_PATH')

    engine = Engine(stockfish_path)
    engine_analyse = engine.analyse(request.get_json()['pgn_code'])
    response = analyse_service.classify_and_evaluate_moves(engine_analyse, polyglot_book_path)
    engine.quit_engine()

    return make_response(jsonify(response), 200)


@board_bp.route('/user/<string:user_name>/archives/import', methods=['POST'])
def import_archives_from_chessdotcom(user_name):
    chessdotcom_service.import_and_save_archives_from_chessdotcom(user_name)
    return make_response('', 200) 


@board_bp.route('/user/<string:user_name>/games/import', methods=['POST'])
def import_games_from_chessdotcom(user_name):
    date_game = dt.datetime.strptime(request.get_json()['date_game'], '%Y/%m').date()
    chessdotcom_service.import_and_save_games_from_chessdotcom(user_name, date_game)
    return make_response('', 200) 


@board_bp.route('/user/<string:user_name>/archives', methods=['GET'])
def get_archives_of_user(user_name):
    archives = chessdotcom_service.get_archives_of_user(user_name)
    return make_response(jsonify(archives), 200)


@board_bp.route('/user/<string:user_name>/games/<int:year>/<int:month>', methods=['GET'])
def get_games_by_month_and_user(user_name, year, month):
    date_game = dt.date(year=year, month=month, day=1)
    games = chessdotcom_service.get_games_by_month_and_user(user_name, date_game)
    return make_response(jsonify(games), 200)

