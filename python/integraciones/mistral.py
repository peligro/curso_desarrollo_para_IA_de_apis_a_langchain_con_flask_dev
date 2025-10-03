from flask import  abort
from http import HTTPStatus
import requests
from dotenv import load_dotenv
import os
# Cargar variables de entorno desde el archivo .env
load_dotenv()


def get_cabeceros_mistral():
    return {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}"
    }


def get_consulta_simple_mistral(prompt):
    data = {
    "model": "mistral-tiny",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
    }
    response = requests.post(
        f"{os.getenv('MISTRAL_BASE_URL')}chat/completions", 
        headers=get_cabeceros_mistral(), 
        json=data
        )
    if response.status_code == 200:
        response_json = response.json()
        # Devolver directamente el contenido del mensaje
        return response_json["choices"][0]["message"]["content"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_consulta_sql_mistral(texto):
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
        "model": "mistral-tiny",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2  # Temperatura baja para respuestas más deterministas
    }

    # Realizar la solicitud a Mistral AI
    response = requests.post(
        f"{os.getenv('MISTRAL_BASE_URL')}chat/completions",
        headers=get_cabeceros_mistral(),
        json=data
    )

    # Procesar la respuesta
    if response.status_code == 200:
        consulta_sql = response.json()["choices"][0]["message"]["content"]
       

        return consulta_sql
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_traduccion_mistral(texto, idioma_destino):
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
        "model": "mistral-small",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    response = requests.post(
        f"{os.getenv('MISTRAL_BASE_URL')}chat/completions",
        headers=get_cabeceros_mistral(),
        json=data
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_analisis_sentimiento_mistral(texto):
    prompt = f"""
    Analiza el sentimiento del siguiente texto:
    {texto}
    Devuelve solo: positivo, negativo o neutral.
    """
    data = {
        "model": "mistral-small",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    response = requests.post(
        f"{os.getenv('MISTRAL_BASE_URL')}chat/completions",
        headers=get_cabeceros_mistral(),
        json=data
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        abort(HTTPStatus.NOT_FOUND)



def get_chat_con_historial_mistral(mensajes_historial ):
    """
    Realiza una consulta a Mistral AI con historial de conversación completo
    mensajes_historial: Lista de mensajes con formato [{"role": "user/assistant", "content": "mensaje"}, ...]
    """
    
    data = {
        "model": "mistral-small",
        "messages": mensajes_historial,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            f"{os.getenv('MISTRAL_BASE_URL')}chat/completions",
            headers=get_cabeceros_mistral(),
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            response_json = response.json()
            return response_json["choices"][0]["message"]["content"]
        else:
            print(f"Error en Mistral API: {response.status_code} - {response.text}")
            abort(HTTPStatus.NOT_FOUND)
            
    except Exception as e:
        print(f"Error en conexión con Mistral: {e}")
        abort(HTTPStatus.NOT_FOUND)