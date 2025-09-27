from flask import Blueprint, request, abort
from http import HTTPStatus


parametros_bp = Blueprint('parametros', __name__)

@parametros_bp.route('/parametros/<int:id>/<slug>')
def parametros_index(id, slug):
    if id <= 0 or not slug.strip():
        return "Recurso no encontrado", HTTPStatus.NOT_FOUND
    
    return f"id={id} | slug={slug}"
    

@parametros_bp.route('/parametros-querystring')
def parametros_querystring():
    # Obtener los parámetros de la query string
    id_str = request.args.get('id')      # str o None
    slug = request.args.get('slug')      # str o None

    # Validar que existan
    if id_str is None or slug is None:
        abort(HTTPStatus.NOT_FOUND)
        #return "Faltan parámetros: se esperan ?id=...&slug=...", HTTPStatus.NOT_FOUND

    # Convertir id a entero (con manejo de error)
    try:
        id = int(id_str)
    except ValueError:
        return "El parámetro 'id' debe ser un número entero", HTTPStatus.NOT_FOUND

    # Validar lógica adicional (opcional)
    if id <= 0 or not slug.strip():
        return "Datos inválidos", HTTPStatus.NOT_FOUND

    return f"id={id} | slug={slug}"