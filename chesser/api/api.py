from .teste import teste_bp
from .view.views import view_bp

def init_app(app):
    teste_bp.config = app.config
    app.register_blueprint(teste_bp)
    app.register_blueprint(view_bp)