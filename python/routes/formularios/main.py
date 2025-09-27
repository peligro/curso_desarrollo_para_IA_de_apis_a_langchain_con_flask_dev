from flask import Blueprint, render_template, request, flash, redirect, url_for
from http import HTTPStatus
from utilidades.utilidades import EMAIL_REGEX


formularios_bp = Blueprint('formularios', __name__)


@formularios_bp.route('/formulario-simple', methods=['GET'])
def formularios_simple():
    
    return render_template('formularios/simple.html')



@formularios_bp.route('/formulario-simple', methods=['POST'])
def formularios_simple_post():
    
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    telefono = request.form.get('telefono', '').strip()

    # Validación: campos obligatorios
    if not nombre or not correo or not telefono:
        flash("Todos los campos son obligatorios.", "danger")
        return render_template('formularios/simple.html'), HTTPStatus.BAD_REQUEST

    # Validación: email
    if not EMAIL_REGEX.match(correo):
        flash("Por favor, ingresa un correo electrónico válido.", "danger")
        return render_template('formularios/simple.html'), HTTPStatus.BAD_REQUEST

    # Validación: teléfono (mínimo 10-15 dígitos, solo números y símbolos permitidos)
    if not telefono.replace('+', '').replace('-', '').replace(' ', '').isdigit():
        flash("El teléfono solo debe contener números, +, - o espacios.", "danger")
        return render_template('formularios/simple.html'), HTTPStatus.BAD_REQUEST

    if len(telefono.replace('+', '').replace('-', '').replace(' ', '')) < 10:
        flash("El teléfono debe tener al menos 10 dígitos.", "danger")
        return render_template('formularios/simple.html'), HTTPStatus.BAD_REQUEST

    flash(f"Datos recibidos nombre={nombre} | correo={correo} | teléfono={telefono}", "success")
    return redirect(url_for('formularios.formularios_simple'))

    


"""
def formularios_simple_post():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    telefono = request.form.get('telefono', '').strip()
    return (f"Datos recibidos nombre={nombre} | correo={correo} | teléfono={telefono}" )
"""

