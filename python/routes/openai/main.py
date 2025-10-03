from flask import Blueprint, render_template, request, flash
from http import HTTPStatus
from integraciones.openai import get_consulta_simple_openai, get_consulta_sql_openai, get_traduccion_openai, get_analisis_sentimiento_openai, get_consulta_imagen_openai, generar_imagen_dall_e_3, transcribir_audio_openai, get_chat_con_historial_openai
from utilidades.utilidades import inicializar_historial, obtener_historial_para_ia, agregar_al_historial, limpiar_historial, obtener_historial_formateado
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


@openai_bp.route('/openai/audio', methods=['GET', 'POST'])
def openai_audio():
    if request.method == 'POST':
        audio_path = request.form.get('audio_path', '').strip()
        
        if not audio_path:
            flash("No se especificó la ruta del audio.", "danger")
            return render_template('openai/audio.html'), HTTPStatus.BAD_REQUEST
        
        # Inicio del timer
        start_time = time.time()

        try:
            # Llamada a la API de OpenAI para transcribir
            respuesta = transcribir_audio_openai(audio_path)
            
            # Fin del timer
            end_time = time.time()
            
            # Calcular el tiempo transcurrido en segundos
            tiempo_transcurrido = round(end_time - start_time, 2)
            
            data = {
                'tiempo_transcurrido': tiempo_transcurrido,
                'respuesta': respuesta
            }
            return render_template('openai/audio.html', **data)
            
        except Exception as e:
            flash(f"Error al transcribir el audio: {str(e)}", "danger")
            return render_template('openai/audio.html'), HTTPStatus.INTERNAL_SERVER_ERROR
    return render_template('openai/audio.html')


@openai_bp.route('/openai/chat-con-historial', methods=['GET', 'POST'])
def openai_chat_con_historial():
    # Inicializar historial al cargar la página
    inicializar_historial()
    
    if request.method == 'POST':
        prompt = request.form.get('prompt', '').strip()
        accion = request.form.get('accion', 'enviar')
        
        # Manejar acción de limpiar historial
        if accion == 'limpiar':
            limpiar_historial()
            flash("Historial limpiado correctamente.", "success")
            return render_template('openai/chat_con_historial.html', 
                                 historial=[],
                                 tiempo_transcurrido='',
                                 respuesta='')
        
        if not prompt:
            flash("El prompt no puede estar vacío.", "danger")
            return render_template('openai/chat_con_historial.html', 
                                 historial=obtener_historial_para_ia(),
                                 tiempo_transcurrido='',
                                 respuesta=''), HTTPStatus.BAD_REQUEST
        
        # Agregar el mensaje del usuario al historial
        agregar_al_historial('usuario', prompt)
        
        # Inicio del timer
        start_time = time.time()

        # Obtener el historial formateado para Ollama
        historial_formateado = obtener_historial_formateado()
        
        # Llamada a la API de Ollama con historial completo
        respuesta = get_chat_con_historial_openai(
            mensajes_historial=historial_formateado 
        )

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido
        tiempo_transcurrido = round(end_time - start_time, 2)
        
        # Agregar la respuesta de la IA al historial
        agregar_al_historial('asistente', respuesta)
        
        data = {
            'tiempo_transcurrido': tiempo_transcurrido,
            'respuesta': respuesta,
            'historial': obtener_historial_para_ia()
        }
        
        return render_template('openai/chat_con_historial.html', **data)
    
    # GET request - mostrar página con historial actual
    data = {
        'tiempo_transcurrido': '',
        'respuesta': '',
        'historial': obtener_historial_para_ia()
    }
    return render_template('openai/chat_con_historial.html', **data)