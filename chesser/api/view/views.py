from flask import render_template, Blueprint

from chesser.service import board_service


view_bp = Blueprint('view', 
                    __name__, 
                    template_folder='templates', 
                    static_folder='static',
                    static_url_path='/view/static')


def init_app(app): app.register_blueprint(view_bp)


@view_bp.route('/board', methods=['GET'])
def index():
    return render_template("board.html", board=board_service.get_board_coordinates())
