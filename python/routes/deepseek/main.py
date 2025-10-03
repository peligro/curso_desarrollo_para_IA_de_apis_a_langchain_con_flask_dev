from flask import Blueprint, render_template, request, flash
from http import HTTPStatus
from integraciones.deepseek import get_consulta_simple_deepseek, get_consulta_sql_deepseek, get_traduccion_deepseek, get_analisis_sentimiento_deepseek, get_chat_con_historial_deepseek
from utilidades.utilidades import inicializar_historial, obtener_historial_para_ia, agregar_al_historial, limpiar_historial, obtener_historial_formateado
import time

deepseek_bp = Blueprint('deepseek', __name__)


@deepseek_bp.route('/deepseek')
def deepseek_index():
    return render_template('deepseek/index.html')


@deepseek_bp.route('/deepseek/prompt', methods=['GET', 'POST'])
def deepseek_prompt():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('deepseek/prompt.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = get_consulta_simple_deepseek(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('deepseek/prompt.html', **data) 
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('deepseek/prompt.html', **data)


@deepseek_bp.route('/deepseek/consulta', methods=['GET', 'POST'])
def deepseek_consulta():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('deepseek/consulta.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = get_consulta_sql_deepseek(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('deepseek/consulta.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('deepseek/consulta.html', **data)



@deepseek_bp.route('/deepseek/traductor', methods=['GET', 'POST'])
def deepseek_traductor():
    if request.method =='POST':
        idioma = request.form.get('idioma', '').strip()
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('deepseek/traductor.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = get_traduccion_deepseek(prompt, idioma)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('deepseek/traductor.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('deepseek/traductor.html', **data)


@deepseek_bp.route('/deepseek/sentimiento', methods=['GET', 'POST'])
def deepseek_sentimiento():
    if request.method =='POST':
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('deepseek/sentimiento.html'), HTTPStatus.BAD_REQUEST
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de openai
        respuesta = get_analisis_sentimiento_deepseek(prompt)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido en milisegundos
        tiempo_transcurrido = round(end_time - start_time, 2)
        data = {
        'tiempo_transcurrido': tiempo_transcurrido,
        'respuesta':respuesta
        }
        return render_template('deepseek/sentimiento.html', **data)
    data = {
        'tiempo_transcurrido': '',
        'respuesta':''
    }
    return render_template('deepseek/sentimiento.html', **data)


@deepseek_bp.route('/deepseek/chat-con-historial', methods=['GET', 'POST'])
def deepseek_chat_con_historial():
    # Inicializar historial al cargar la página
    inicializar_historial()
    
    if request.method == 'POST':
        prompt = request.form.get('prompt', '').strip()
        accion = request.form.get('accion', 'enviar')
        
        # Manejar acción de limpiar historial
        if accion == 'limpiar':
            limpiar_historial()
            flash("Historial limpiado correctamente.", "success")
            return render_template('deepseek/chat_con_historial.html', 
                                 historial=[],
                                 tiempo_transcurrido='',
                                 respuesta='')
        
        if not prompt:
            flash("El prompt no puede estar vacío.", "danger")
            return render_template('deepseek/chat_con_historial.html', 
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
        respuesta = get_chat_con_historial_deepseek(
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
        
        return render_template('deepseek/chat_con_historial.html', **data)
    
    # GET request - mostrar página con historial actual
    data = {
        'tiempo_transcurrido': '',
        'respuesta': '',
        'historial': obtener_historial_para_ia()
    }
    return render_template('deepseek/chat_con_historial.html', **data)