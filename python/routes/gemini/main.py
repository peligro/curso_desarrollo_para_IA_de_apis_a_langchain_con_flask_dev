from flask import Blueprint, render_template, request, flash
from http import HTTPStatus
from integraciones.gemini import get_consulta_simple_gemini, get_consulta_sql_gemini, get_traduccion_gemini, get_analisis_sentimiento_gemini, get_consulta_imagen_gemini, transcribir_audio_gemini
import time


gemini_bp = Blueprint('gemini', __name__)


@gemini_bp.route('/gemini')
def gemini_index():
    return render_template('gemini/index.html')


@gemini_bp.route('/gemini/prompt', methods=['GET', 'POST'])
def gemini_prompt():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('gemini/prompt.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de gemini
        respuesta = get_consulta_simple_gemini(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('gemini/prompt.html', **data) 
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('gemini/prompt.html', **data)


@gemini_bp.route('/gemini/consulta', methods=['GET', 'POST'])
def gemini_consulta():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('gemini/consulta.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de gemini
        respuesta = get_consulta_sql_gemini(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('gemini/consulta.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('gemini/consulta.html', **data)


@gemini_bp.route('/gemini/traductor', methods=['GET', 'POST'])
def gemini_traductor():
    if request.method =='POST':
        idioma = request.form.get('idioma', '').strip()
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('gemini/traductor.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de gemini
        respuesta = get_traduccion_gemini(prompt, idioma)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('gemini/traductor.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('gemini/traductor.html', **data)


@gemini_bp.route('/gemini/sentimiento', methods=['GET', 'POST'])
def gemini_sentimiento():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('gemini/sentimiento.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de gemini
        respuesta = get_analisis_sentimiento_gemini(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('gemini/sentimiento.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('gemini/sentimiento.html', **data)



@gemini_bp.route('/gemini/reconocimiento', methods=['GET', 'POST'])
def gemini_reconocimiento():
    if request.method =='POST':
        url = request.form.get('url', '').strip()
        prompt = request.form.get('url', '').strip()
        if not prompt or not url:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('gemini/reconocimiento.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de gemini
        respuesta = get_consulta_imagen_gemini(prompt, url)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('gemini/reconocimiento.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('gemini/reconocimiento.html', **data)



@gemini_bp.route('/gemini/audio', methods=['GET', 'POST'])
def gemini_audio():
    if request.method == 'POST':
        audio_path = request.form.get('audio_path', '').strip()
        
        if not audio_path:
            flash("No se especificó la ruta del audio.", "danger")
            return render_template('gemini/audio.html'), HTTPStatus.BAD_REQUEST
        
        # Inicio del timer
        start_time = time.time()

        try:
            # Llamada a la API de OpenAI para transcribir
            respuesta = transcribir_audio_gemini(audio_path)
            
            # Fin del timer
            end_time = time.time()
            
            # Calcular el tiempo transcurrido en segundos
            tiempo_transcurrido = round(end_time - start_time, 2)
            
            data = {
                'tiempo_transcurrido': tiempo_transcurrido,
                'respuesta': respuesta
            }
            return render_template('gemini/audio.html', **data)
            
        except Exception as e:
            flash(f"Error al transcribir el audio: {str(e)}", "danger")
            return render_template('gemini/audio.html'), HTTPStatus.INTERNAL_SERVER_ERROR
    return render_template('gemini/audio.html')