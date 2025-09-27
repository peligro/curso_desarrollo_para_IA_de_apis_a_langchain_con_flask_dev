from flask import  abort
from http import HTTPStatus
import requests
from dotenv import load_dotenv
import os
# Cargar variables de entorno desde el archivo .env
load_dotenv()


def get_cabeceros():
    return {
    "Content-Type": "application/json",
    }


def get_consulta_simple_gemini(pregunta):


    payload = {
        'contents': [
            {
                'parts': [
                    {'text': pregunta}
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.7,
            'maxOutputTokens': 500,
        }
    }

    try:
        response = requests.post(
            f"{os.getenv('GEMINI_BASE_URL')}models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers=get_cabeceros(),
            json=payload
        )
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP

        data = response.json()
        respuesta_ia = data['candidates'][0]['content']['parts'][0]['text']
        return respuesta_ia
    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.NOT_FOUND)



def get_consulta_sql_gemini(texto):
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
    - Solo devuelve la consulta SQL, sin explicaciones ni comentarios, ni al inicio ni al final.
    """

    

    payload = {
        'contents': [
            {
                'parts': [
                    {'text': prompt}
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.2,  # Temperatura baja para respuestas más deterministas
            'maxOutputTokens': 500,
        }
    }

    try:
        response = requests.post(
            f"{os.getenv('GEMINI_BASE_URL')}models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers=get_cabeceros(),
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        consulta_sql = data['candidates'][0]['content']['parts'][0]['text']

        # Procesar la respuesta para limpiar el formato
        consulta_sql = consulta_sql.strip()
        if consulta_sql.startswith("```sql"):
            consulta_sql = consulta_sql[5:].strip()
        if consulta_sql.endswith("```"):
            consulta_sql = consulta_sql[:-3].strip()
        if consulta_sql and not consulta_sql[0].isalpha() and not consulta_sql[0] == "S":
            consulta_sql = consulta_sql[1:].strip()

        return consulta_sql

    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.NOT_FOUND)


def get_traduccion_gemini(texto, idioma_destino):
    prompt = f"""
    Traduce el siguiente texto al {idioma_destino}:
    {texto}
    Reglas:
    - Mantén el tono y estilo del texto original.
    - Solo devuelve la traducción, sin explicaciones adicionales, ni al inicio ni al final.
    - No muestres ninguna nota ni al final ni al inicio, sólo devuelve la traducción, de ningún tipo.
    - No muestres indicaciones referentes al tipo de caracteres usados, ni advertencias.
    """

   
 
    payload = {
        'contents': [
            {
                'parts': [
                    {'text': prompt}
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.3,  # Temperatura baja para mantener coherencia
            'maxOutputTokens': 500,
        }
    }

    try:
        response = requests.post(
            f"{os.getenv('GEMINI_BASE_URL')}models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers=get_cabeceros(),
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        traduccion = data['candidates'][0]['content']['parts'][0]['text']

        # Limpiar la respuesta según las reglas
        traduccion = traduccion.strip()
        if traduccion.startswith('"') and traduccion.endswith('"'):
            traduccion = traduccion[1:-1]
        if traduccion.startswith("```"):
            traduccion = traduccion[3:].strip()
        if traduccion.endswith("```"):
            traduccion = traduccion[:-3].strip()

        return traduccion

    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.NOT_FOUND)


def get_analisis_sentimiento_gemini(texto):
    prompt = f"""
    Analiza el sentimiento del siguiente texto:
    {texto}
    Devuelve solo: positivo, negativo o neutral.
    """


   

    payload = {
        'contents': [
            {
                'parts': [
                    {'text': prompt}
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.2,  # Temperatura baja para respuestas deterministas
            'maxOutputTokens': 10,  # Suficiente para "positivo", "negativo" o "neutral"
        }
    }

    try:
        response = requests.post(
            f"{os.getenv('GEMINI_BASE_URL')}models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers=get_cabeceros(),
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        sentimiento = data['candidates'][0]['content']['parts'][0]['text']

        # Limpiar la respuesta para asegurar que solo devuelva "positivo", "negativo" o "neutral"
        #sentimiento = sentimiento.strip().lower()
        #if sentimiento not in ["positivo", "negativo", "neutral"]:
        #    return "neutral"  # Valor por defecto si la respuesta no es válida

        return sentimiento

    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.NOT_FOUND)