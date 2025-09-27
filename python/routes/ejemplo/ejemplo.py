from flask import Blueprint

ejemplo_bp = Blueprint('ejemplo', __name__)

@ejemplo_bp.route('/ejemplo')
def ejemplo():
    return "ejemplosssss con carpeta"