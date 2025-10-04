from flask import Blueprint, render_template, request, flash
from http import HTTPStatus
from integraciones.perplexity_service import get_busqueda_basica_perplexity, get_investigacion_avanzada_perplexity, get_parametros_investigacion_perplexity, get_chat_con_historial_perplexity, get_busqueda_comparativa_perplexity, get_formatos_cita_disponibles, get_citas_automaticas_perplexity
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


@perplexity_bp.route('/perplexity/investigacion-avanzada', methods=['GET', 'POST'])
def perplexity_investigacion_avanzada():
    if request.method == 'POST':
        pregunta = request.form.get('pregunta', '').strip()
        dominio = request.form.get('dominio', '')
        fecha = request.form.get('fecha', '')
        idioma = request.form.get('idioma', '')
        enfoque = request.form.get('enfoque', '')
        profundidad = request.form.get('profundidad', '')
        max_tokens = int(request.form.get('max_tokens', 1500))
        
        if not pregunta:
            flash("La pregunta no puede estar vacía.", "danger")
            return render_template('perplexity/investigacion_avanzada.html', 
                                 parametros=get_parametros_investigacion_perplexity()), HTTPStatus.BAD_REQUEST
        
        # Construir parámetros personalizados
        parametros_personalizados = {
            'max_tokens': max_tokens
        }
        
        # Agregar parámetros opcionales
        if dominio:
            parametros_personalizados['search_domain'] = dominio
        if fecha:
            parametros_personalizados['date_range'] = fecha
        if idioma:
            parametros_personalizados['language'] = idioma
        if enfoque:
            parametros_personalizados['focus'] = enfoque
        
        # Ajustar temperatura según profundidad
        if profundidad == 'rapida':
            parametros_personalizados['temperature'] = 0.1
        elif profundidad == 'profunda':
            parametros_personalizados['temperature'] = 0.4
            parametros_personalizados['max_tokens'] = 2000
        else:  # balanceada
            parametros_personalizados['temperature'] = 0.3
        
        # Inicio del timer
        start_time = time.time()

        # Llamada a la API de Perplexity
        resultado = get_investigacion_avanzada_perplexity(pregunta, parametros_personalizados)

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido
        tiempo_transcurrido = round(end_time - start_time, 2)
        
        data = {
            'tiempo_transcurrido': tiempo_transcurrido,
            'resultado': resultado,
            'pregunta_original': pregunta,
            'parametros_usados': parametros_personalizados,
            'parametros': get_parametros_investigacion_perplexity()
        }
        
        return render_template('perplexity/investigacion_avanzada.html', **data)
    
    # GET request
    data = {
        'tiempo_transcurrido': '',
        'resultado': None,
        'pregunta_original': '',
        'parametros_usados': {},
        'parametros': get_parametros_investigacion_perplexity()
    }
    return render_template('perplexity/investigacion_avanzada.html', **data)



@perplexity_bp.route('/perplexity/chat-con-historial', methods=['GET', 'POST'])
def perplexity_chat_con_historial():
    # Inicializar historial al cargar la página
    inicializar_historial()
    
    if request.method == 'POST':
        prompt = request.form.get('prompt', '').strip()
        accion = request.form.get('accion', 'enviar')
        
        # Manejar acción de limpiar historial
        if accion == 'limpiar':
            limpiar_historial()
            flash("Historial de chat limpiado correctamente.", "success")
            return render_template('perplexity/chat_con_historial.html', 
                                 historial=[],
                                 tiempo_transcurrido='',
                                 respuesta='')
        
        if not prompt:
            flash("El mensaje no puede estar vacío.", "danger")
            return render_template('perplexity/chat_con_historial.html', 
                                 historial=obtener_historial_para_ia(),
                                 tiempo_transcurrido='',
                                 respuesta=''), HTTPStatus.BAD_REQUEST
        
        # Agregar el mensaje del usuario al historial
        agregar_al_historial('usuario', prompt)
        
        # Inicio del timer
        start_time = time.time()

        # Obtener el historial formateado para Perplexity
        historial_formateado = obtener_historial_formateado()
        
        # Llamada a la API de Perplexity con historial completo
        resultado = get_chat_con_historial_perplexity(
            mensajes_historial=historial_formateado
        )

        # Fin del timer
        end_time = time.time()
        
        # Calcular el tiempo transcurrido
        tiempo_transcurrido = round(end_time - start_time, 2)
        
        # Agregar la respuesta de Perplexity al historial
        if not resultado.get('error', False):
            agregar_al_historial('asistente', resultado['respuesta'])
        
        data = {
            'tiempo_transcurrido': tiempo_transcurrido,
            'resultado': resultado,
            'historial': obtener_historial_para_ia()
        }
        
        return render_template('perplexity/chat_con_historial.html', **data)
    
    # GET request - mostrar página con historial actual
    data = {
        'tiempo_transcurrido': '',
        'resultado': None,
        'historial': obtener_historial_para_ia()
    }
    return render_template('perplexity/chat_con_historial.html', **data)



@perplexity_bp.route('/perplexity/busqueda-comparativa', methods=['GET', 'POST'])
def perplexity_busqueda_comparativa():
    if request.method == 'POST':
        pregunta = request.form.get('pregunta', '').strip()
        incluir_analisis = request.form.get('incluir_analisis', 'true') == 'true'
        
        if not pregunta:
            flash("La pregunta no puede estar vacía.", "danger")
            return render_template('perplexity/busqueda_comparativa.html'), HTTPStatus.BAD_REQUEST
        
        # Inicio del timer general
        start_time = time.time()

        # Llamada a la función de búsqueda comparativa
        resultado_comparativo = get_busqueda_comparativa_perplexity(pregunta, incluir_analisis)

        # Fin del timer
        end_time = time.time()
        tiempo_total = round(end_time - start_time, 2)
        
        data = {
            'tiempo_total': tiempo_total,
            'resultado': resultado_comparativo,
            'pregunta_original': pregunta,
            'incluir_analisis': incluir_analisis
        }
        
        return render_template('perplexity/busqueda_comparativa.html', **data)
    
    # GET request
    data = {
        'tiempo_total': '',
        'resultado': None,
        'pregunta_original': '',
        'incluir_analisis': True
    }
    return render_template('perplexity/busqueda_comparativa.html', **data)



@perplexity_bp.route('/perplexity/citas-automaticas', methods=['GET', 'POST'])
def perplexity_citas_automaticas():
    if request.method == 'POST':
        texto = request.form.get('texto', '').strip()
        formato_cita = request.form.get('formato_cita', 'apa')
        incluir_resumen = request.form.get('incluir_resumen', 'true') == 'true'
        
        if not texto:
            flash("El texto no puede estar vacío.", "danger")
            return render_template('perplexity/citas_automaticas.html', 
                                 formatos=get_formatos_cita_disponibles()), HTTPStatus.BAD_REQUEST
        
        # Inicio del timer
        start_time = time.time()

        # Llamada a la función de citas automáticas
        resultado_citas = get_citas_automaticas_perplexity(texto, formato_cita, incluir_resumen)

        # Fin del timer
        end_time = time.time()
        tiempo_total = round(end_time - start_time, 2)
        
        data = {
            'tiempo_total': tiempo_total,
            'resultado': resultado_citas,
            'texto_original': texto,
            'formato_seleccionado': formato_cita,
            'incluir_resumen': incluir_resumen,
            'formatos': get_formatos_cita_disponibles()
        }
        
        return render_template('perplexity/citas_automaticas.html', **data)
    
    # GET request
    data = {
        'tiempo_total': '',
        'resultado': None,
        'texto_original': '',
        'formato_seleccionado': 'apa',
        'incluir_resumen': True,
        'formatos': get_formatos_cita_disponibles()
    }
    return render_template('perplexity/citas_automaticas.html', **data)