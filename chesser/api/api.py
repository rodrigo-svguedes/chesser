from .board import board_bp
from .view.views import view_bp

def init_app(app):
    board_bp.config = app.config
    app.register_blueprint(board_bp)
    app.register_blueprint(view_bp)