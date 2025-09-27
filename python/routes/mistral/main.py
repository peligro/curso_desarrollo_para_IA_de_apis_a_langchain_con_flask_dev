from flask import Blueprint, render_template, request, flash
from http import HTTPStatus
from integraciones.mistral import get_consulta_simple_mistral
import time


mistral_bp = Blueprint('mistral', __name__)


@mistral_bp.route('/mistral')
def mistral_index():
    return render_template('mistral/index.html')


@mistral_bp.route('/mistral/prompt', methods=['GET', 'POST'])
def mistral_prompt():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('mistral/prompt.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de Mistral
        respuesta = get_consulta_simple_mistral(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'method':'GET',
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('mistral/prompt.html', **data) 
    data = {
        'method':'POST',
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('mistral/prompt.html', **data)

