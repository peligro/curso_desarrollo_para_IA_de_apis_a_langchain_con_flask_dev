import re
import pycurl
from io import BytesIO

#sesiones
from flask import session
import time


# Expresión regular para validar email (básica pero efectiva)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def descargar_imagen_con_curl(url):
    """
    Descarga una imagen usando pycurl y devuelve el contenido binario.
    """
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.SSL_VERIFYPEER, False)
    c.setopt(c.SSL_VERIFYHOST, False)
    try:
        c.perform()
        http_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        if http_code == 200:
            return buffer.getvalue()
        else:
            raise Exception(f"Error al descargar la imagen (HTTP {http_code})")
    except Exception as e:
        c.close()
        raise Exception(f"Error al descargar la imagen: {str(e)}")
    

#############SESIONES


def inicializar_historial():
    if 'historial_chat' not in session:
        session['historial_chat'] = []
        session['contador_mensajes'] = 0


def agregar_al_historial(rol, mensaje):
    inicializar_historial()
    
    mensaje_data = {
        'id': session['contador_mensajes'],
        'rol': rol,
        'mensaje': mensaje,
        'timestamp': time.time()
    }
    
    session['historial_chat'].append(mensaje_data)
    session['contador_mensajes'] += 1
    
    # Mantener solo los últimos N mensajes para no saturar la sesión
    if len(session['historial_chat']) > 20:  # Últimos 20 mensajes
        session['historial_chat'] = session['historial_chat'][-20:]
    
    # Marcar la sesión como modificada
    session.modified = True


def obtener_historial_para_ia():
    inicializar_historial()
    return session['historial_chat']

# Función para limpiar el historial
def limpiar_historial():
    session['historial_chat'] = []
    session['contador_mensajes'] = 0
    session.modified = True


def obtener_historial_formateado():
    """
    Convierte el historial de la sesión al formato que espera la API de Ollama
    Returns: Lista de mensajes en formato [{"role": "user/assistant", "content": "mensaje"}]
    """
    inicializar_historial()
    
    mensajes_formateados = []
    for mensaje in session['historial_chat']:
        # Convertir nuestro formato interno al formato de Ollama
        role = "user" if mensaje['rol'] == 'usuario' else "assistant"
        mensajes_formateados.append({
            "role": role,
            "content": mensaje['mensaje']
        })
    
    return mensajes_formateados


def obtener_historial_formateado_gemini():
    """
    Convierte el historial de la sesión al formato que espera la API de Gemini
    Returns: Lista de mensajes en formato [{"role": "user/model", "content": "mensaje"}]
    """
    inicializar_historial()
    
    mensajes_formateados = []
    for mensaje in session['historial_chat']:
        # Convertir nuestro formato interno al formato de Gemini
        # Gemini usa 'user' para humano y 'model' para la IA
        role = "user" if mensaje['rol'] == 'usuario' else "model"
        mensajes_formateados.append({
            "role": role,
            "content": mensaje['mensaje']
        })
    
    return mensajes_formateados


def obtener_historial_formateado_claude():
    """
    Convierte el historial de la sesión al formato que espera la API de Claude
    Returns: Lista de mensajes en formato [{"role": "user/assistant", "content": "mensaje"}]
    """
    inicializar_historial()
    
    mensajes_formateados = []
    for mensaje in session['historial_chat']:
        # Convertir nuestro formato interno al formato de Claude
        # Claude usa 'user' para humano y 'assistant' para la IA
        role = "user" if mensaje['rol'] == 'usuario' else "assistant"
        mensajes_formateados.append({
            "role": role,
            "content": mensaje['mensaje']
        })
    
    return mensajes_formateados



############FIN SESIONES