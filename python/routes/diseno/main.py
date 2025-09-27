from flask import Blueprint, render_template
from http import HTTPStatus


diseno_bp = Blueprint('diseno', __name__)


@diseno_bp.route('/diseno')
def diseno_index():
    #return f"diseno"
    data = {
        'title': 'Inicio',
        'mensaje': '¡Hola desde Flask + Jinja!',
        'html':'texto con <strong>negritas</strong>'
    }
    return render_template('diseno/index.html', **data)


"""
def diseno_index():
    return render_template('diseno/index.html', **{
        'title': 'Inicio',
        'mensaje': '¡Hola desde Flask + Jinja!'})
""" 


@diseno_bp.route('/condiciones')
def diseno_condiciones():
    data = {
        'edad': 14
    }
    return render_template('diseno/condiciones.html', **data)


@diseno_bp.route('/ciclos')
def diseno_ciclos():
    
    return render_template('diseno/ciclos.html')


@diseno_bp.route('/arreglo')
def diseno_arreglo():
    paises = ["Chile", "México", "Venezuela", "Perú", "Bolivia", "España"]
    
    # Ejemplo 2: lista de diccionarios (muy común en apps reales)
    personas = [
        {"nombre": "César Cancino", "edad": 45},
        {"nombre": "Luis Muñoz", "edad": 35},
        {"nombre": "Carla Martínez", "edad": 22}
    ]
    
    data = {
        'paises': paises,
        'personas': personas
    }
    return render_template('diseno/arreglo.html', **data)
