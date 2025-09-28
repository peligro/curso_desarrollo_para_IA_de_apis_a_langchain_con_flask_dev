from flask import Blueprint, render_template, request, flash
from http import HTTPStatus
from integraciones.openai import get_consulta_simple_openai, get_consulta_sql_openai, get_traduccion_openai, get_analisis_sentimiento_openai, get_consulta_imagen_openai, generar_imagen_dall_e_3
import time

from dotenv import load_dotenv
load_dotenv()
import os


openai_bp = Blueprint('openai', __name__)


@openai_bp.route('/openai')
def openai_index():
    return render_template('openai/index.html')


@openai_bp.route('/openai/prompt', methods=['GET', 'POST'])
def openai_prompt():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('openai/prompt.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = get_consulta_simple_openai(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('openai/prompt.html', **data) 
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('openai/prompt.html', **data)


@openai_bp.route('/openai/consulta', methods=['GET', 'POST'])
def openai_consulta():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('openai/consulta.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = get_consulta_sql_openai(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('openai/consulta.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('openai/consulta.html', **data)



@openai_bp.route('/openai/traductor', methods=['GET', 'POST'])
def openai_traductor():
    if request.method =='POST':
        idioma = request.form.get('idioma', '').strip()
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('openai/traductor.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = get_traduccion_openai(prompt, idioma)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('openai/traductor.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('openai/traductor.html', **data)


@openai_bp.route('/openai/sentimiento', methods=['GET', 'POST'])
def openai_sentimiento():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('openai/sentimiento.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = get_analisis_sentimiento_openai(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('openai/sentimiento.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('openai/sentimiento.html', **data)


@openai_bp.route('/openai/reconocimiento', methods=['GET', 'POST'])
def openai_reconocimiento():
    if request.method =='POST':
        url = request.form.get('url', '').strip()
        prompt = request.form.get('url', '').strip()
        if not prompt or not url:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('openai/reconocimiento.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de gemini
        respuesta = get_consulta_imagen_openai(prompt, url)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('openai/reconocimiento.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('openai/reconocimiento.html', **data)


@openai_bp.route('/openai/dall-e-3', methods=['GET', 'POST'])
def openai_dall_e_3():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('openai/dall_e_3.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = generar_imagen_dall_e_3(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta,
        'bucket':os.getenv('AWS_BUCKET')
        }
        return render_template('openai/dall_e_3.html', **data) 
    data = {
        'tiempo_transcurrido': '',
        'respuesta':'',
        'bucket':os.getenv('AWS_BUCKET')
    }
    return render_template('openai/dall_e_3.html', **data)