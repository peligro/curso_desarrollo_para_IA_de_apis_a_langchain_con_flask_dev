from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def main_index():
    return "hola desde main con carpeta"

@main_bp.route('/nosotros')
def main_nosotros():
    return "Acerca de nosotros con carpeta"