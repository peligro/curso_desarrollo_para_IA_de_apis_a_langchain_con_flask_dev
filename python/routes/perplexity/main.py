from flask import Blueprint, render_template, request, flash
from http import HTTPStatus
from integraciones.perplexity_service import get_busqueda_basica_perplexity
from utilidades.utilidades import inicializar_historial, obtener_historial_para_ia, agregar_al_historial, limpiar_historial, obtener_historial_formateado
import time


perplexity_bp = Blueprint('perplexity', __name__)


@perplexity_bp.route('/perplexity')
def perplexity_index():
    return render_template('perplexity/index.html')


@perplexity_bp.route('/perplexity/busqueda', methods=['GET', 'POST'])
def perplexity_busqueda():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('perplexity/busqueda.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de perplexity
        respuesta = get_busqueda_basica_perplexity(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('perplexity/busqueda.html', **data) 
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('perplexity/busqueda.html', **data)


