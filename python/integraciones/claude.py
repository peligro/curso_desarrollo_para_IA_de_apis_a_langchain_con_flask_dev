from flask import  abort
from http import HTTPStatus
import requests
from dotenv import load_dotenv
import os
# Cargar variables de entorno desde el archivo .env
load_dotenv()


def get_cabeceros_claude():
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
        headers=get_cabeceros_claude(), 
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
        headers=get_cabeceros_claude(), 
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
        headers=get_cabeceros_claude(), 
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
        headers=get_cabeceros_claude(), 
        json=data
        )
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        abort(HTTPStatus.NOT_FOUND)