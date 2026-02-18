from .board import board_bp
from .view.views import view_bp

def init_app(app):
    app.register_blueprint(board_bp)
    app.register_blueprint(view_bp)