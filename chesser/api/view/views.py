from flask import render_template, Blueprint

from chesser.service import board_service


view_bp = Blueprint('view', __name__, url_prefix='', template_folder='templates')

@view_bp.route('/board', methods=['GET'])
def index():
    return render_template("board.html", board=board_service.get_board_coordinates())