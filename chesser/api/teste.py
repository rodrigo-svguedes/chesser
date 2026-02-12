from flask import Blueprint, request, make_response, jsonify

teste_bp = Blueprint('teste', __name__, url_prefix='/teste')

@teste_bp.route('/teste', methods=['GET'])
def save_tipo_essencia():
    return make_response('testadoss', 200)