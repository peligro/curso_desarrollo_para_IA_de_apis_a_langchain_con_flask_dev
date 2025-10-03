from flask import  abort
from http import HTTPStatus
import requests
import base64

from dotenv import load_dotenv
import os
# Cargar variables de entorno desde el archivo .env
load_dotenv()


def get_cabeceros():
    return {
    "anthropic-version":"2023-06-01",
    "Content-Type": "application/json",
    "x-api-key": f"{os.getenv('CLAUDE_API_KEY')}"
    }


def get_consulta_simple_claude(prompt):
    data = {
    "model": "claude-3-haiku-20240307",
    "max_tokens":100,
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
    }
    response = requests.post(
        f"{os.getenv('CLAUDE_BASE_URL')}messages", 
        headers=get_cabeceros(), 
        json=data
        )
    if response.status_code == 200:
        response_json = response.json()
        # Devolver directamente el contenido del mensaje
        return response_json["content"][0]["text"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_consulta_sql_claude(texto):
    schema = """
        Tabla: users
        Columnas:
        - id (int)
        - name (string)
        - email (string)
        - state_id (int)
        - created_at (datetime)
        """
    prompt = f"""
    Eres un experto en bases de datos PostgreSQL. Tu tarea es convertir este texto en una consulta SQL válida:

    Texto: "{texto}"

    Esquema de la tabla:
    {schema}

    Reglas de formato:
    - Nunca uses * en las consultas SQL.
    - Siempre ordena los datos por el id de forma descendente.
    - Solo devuelve la consulta SQL, sin explicaciones ni comentarios, ni al inicio ni al final
    - no envuelvas la consulta en ```sql ```
    """

    # Datos para la solicitud
    data = {
    "model": "claude-3-haiku-20240307",
    "max_tokens":100,
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
    }
    response = requests.post(
        f"{os.getenv('CLAUDE_BASE_URL')}messages", 
        headers=get_cabeceros(), 
        json=data
        )

    # Procesar la respuesta
    if response.status_code == 200:
        consulta_sql = response.json()["content"][0]["text"]
       

        return consulta_sql
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_traduccion_claude(texto, idioma_destino):
    prompt = f"""
    Traduce el siguiente texto al {idioma_destino}:
    {texto}
    Reglas:
    - Mantén el tono y estilo del texto original.
    - Solo devuelve la traducción, sin explicaciones adicionales, ni al inicio ni al final.
    - no muestras ninguna nota ni al final ni al inicio, sólo devuelve la traducción, de ningún tipo.
    - no muestres tampoco indicaciones referentes al tipo de caracteres usados, ni tampoco ninguna advertencia
    """
    data = {
    "model": "claude-3-haiku-20240307",
    "max_tokens":100,
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
    }
    response = requests.post(
        f"{os.getenv('CLAUDE_BASE_URL')}messages", 
        headers=get_cabeceros(), 
        json=data
        )
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_analisis_sentimiento_claude(texto):
    prompt = f"""
    Analiza el sentimiento del siguiente texto:
    {texto}
    Devuelve solo: positivo, negativo o neutral.
    """
    data = {
    "model": "claude-3-haiku-20240307",
    "max_tokens":100,
    "temperature": 0.3,
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
    }
    response = requests.post(
        f"{os.getenv('CLAUDE_BASE_URL')}messages", 
        headers=get_cabeceros(), 
        json=data
        )
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_consulta_imagen_claude(pregunta, url_imagen):
    
    try:
        response_imagen = requests.get(url_imagen)
        response_imagen.raise_for_status()
        
        imagen_base64 = base64.b64encode(response_imagen.content).decode('utf-8')
        content_type = response_imagen.headers.get('content-type', 'image/jpeg')
        
    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.BAD_REQUEST, description=f"Error al descargar la imagen: {str(e)}")

    # Prompt optimizado para evitar bloqueos
    prompt_optimizado = f"""
    Analiza esta imagen de manera objetiva y descriptiva.
    
    Enfócate en:
    - Elementos visuales observables
    - personas, cómo están vestidas, qué están haciendo
    
    Evita cualquier interpretación médica, emocional o personal.
    
    Pregunta específica: {pregunta}
    """
    media_type_mapping = {
        'image/jpeg': 'image/jpeg',
        'image/jpg': 'image/jpeg',
        'image/png': 'image/png',
        'image/gif': 'image/gif',
        'image/webp': 'image/webp'
    }
    
    media_type = media_type_mapping.get(content_type.lower(), 'image/jpeg')
    
    data = {
        "model": "claude-3-haiku-20240307",  # o claude-3-opus-20240229 para mejor análisis
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": imagen_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt_optimizado
                    }
                ]
            }
        ]
    }

    response = requests.post(
        f"{os.getenv('CLAUDE_BASE_URL')}messages", 
        headers=get_cabeceros(), 
        json=data
        )
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Body: {response.text[:500]}") 
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_chat_con_historial_claude(mensajes_historial):
    """
    Realiza una consulta a Claude AI con historial de conversación completo
    mensajes_historial: Lista de mensajes con formato [{"role": "user/assistant", "content": "mensaje"}, ...]
    """
    
    # Convertir el formato de historial al que espera Claude
    messages = []
    
    for mensaje in mensajes_historial:
        # Claude usa 'user' para humano y 'assistant' para la IA
        role = mensaje['role']  # Ya está en el formato correcto
        content = mensaje['content']
        
        # Claude espera el contenido como texto simple
        messages.append({
            "role": role,
            "content": content
        })
    
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1000,
        "temperature": 0.3,
        "messages": messages
    }
    
    try:
        response = requests.post(
            f"{os.getenv('CLAUDE_BASE_URL')}messages",
            headers=get_cabeceros(),
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            response_json = response.json()
            return response_json["content"][0]["text"]
        else:
            print(f"Error en Claude API: {response.status_code} - {response.text}")
            abort(HTTPStatus.NOT_FOUND)
            
    except Exception as e:
        print(f"Error en conexión con Claude: {e}")
        abort(HTTPStatus.NOT_FOUND)