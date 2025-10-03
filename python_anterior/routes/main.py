from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "hola desde main"

@main_bp.route('/nosotros')
def nosotros():
    return "Acerca de nosotros"