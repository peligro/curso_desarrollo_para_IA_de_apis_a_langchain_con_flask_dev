from flask import  abort
from http import HTTPStatus
import requests
import base64
from dotenv import load_dotenv
import os
# Cargar variables de entorno desde el archivo .env
load_dotenv()

from utilidades.utilidades import descargar_imagen_con_curl

#aws 
from aws.aws import get_conection

import time


def get_cabeceros_openai():
    return {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }


def get_consulta_simple_openai(prompt):
    data = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
    }
    response = requests.post(
        f"{os.getenv('OPENAI_API_URL')}chat/completions", 
        headers=get_cabeceros_openai(), 
        json=data
        )
    if response.status_code == 200:
        response_json = response.json()
        # Devolver directamente el contenido del mensaje
        return response_json["choices"][0]["message"]["content"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_consulta_sql_openai(texto):
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
    - Solo devuelve la consulta SQL, sin explicaciones ni comentarios, mi anotaciones Markdown, ni al inicio ni al final
    - no envuelvas la consulta en ```sql ```
    """

    # Datos para la solicitud
    data = {
        "model": "gpt-4o-mini",
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
        f"{os.getenv('OPENAI_API_URL')}chat/completions",
        headers=get_cabeceros_openai(),
        json=data
    )

    # Procesar la respuesta
    if response.status_code == 200:
        consulta_sql = response.json()["choices"][0]["message"]["content"]
        

        return consulta_sql
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_traduccion_openai(texto, idioma_destino):
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
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    response = requests.post(
        f"{os.getenv('OPENAI_API_URL')}chat/completions",
        headers=get_cabeceros_openai(),
        json=data
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_analisis_sentimiento_openai(texto):
    prompt = f"""
    Analiza el sentimiento del siguiente texto:
    {texto}
    Devuelve solo: positivo, negativo o neutral.
    """
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    response = requests.post(
        f"{os.getenv('OPENAI_API_URL')}chat/completions",
        headers=get_cabeceros_openai(),
        json=data
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        abort(HTTPStatus.NOT_FOUND)


def get_consulta_imagen_openai(pregunta, url_imagen):
    try:
        # Descargar la imagen y convertirla a base64
        response_imagen = requests.get(url_imagen)
        response_imagen.raise_for_status()
        imagen_base64 = base64.b64encode(response_imagen.content).decode('utf-8')
    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.BAD_REQUEST, description=f"Error al descargar la imagen: {str(e)}")

    # Prompt optimizado para OpenAI
    prompt_optimizado = f"""
    Analiza esta imagen de manera objetiva y descriptiva.

    Enfócate en:
    - Elementos visuales observables
    - Personas, cómo están vestidas, qué están haciendo

    Evita cualquier interpretación médica, emocional o personal.

    Pregunta específica: {pregunta}
    """

    # Estructura del payload para OpenAI
    payload = {
        "model": "gpt-4o",  # o "gpt-4o" si prefieres el modelo más grande
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_optimizado},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{imagen_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            f"{os.getenv('OPENAI_API_URL')}chat/completions",
            headers=get_cabeceros_openai(),
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        # Verificar si hay errores en la respuesta
        if "error" in data:
            return f"Error al analizar la imagen: {data['error']['message']}"

        respuesta_ia = data["choices"][0]["message"]["content"]
        return respuesta_ia

    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.NOT_FOUND)



def generar_imagen_dall_e_3___(prompt):
    """
    Genera una imagen usando DALL-E 3 y devuelve la URL de la imagen generada.

    Args:
        prompt (str): Descripción de la imagen que se quiere generar.

    Returns:
        str: URL de la imagen generada.
    """
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": "1024x1024",
        "quality": "standard",
        "n": 1,
    }

    try:
        response = requests.post(
            f"{os.getenv('OPENAI_API_URL')}images/generations",
            headers=get_cabeceros_openai(),
            json=data
        )

        if response.status_code == 200:
            response_json = response.json()
            imagen_url=response_json["data"][0]["url"]
            return imagen_url
        else:
            abort(HTTPStatus.BAD_REQUEST, description=f"Error al generar la imagen: {response.text}")

    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.NOT_FOUND)





def generar_imagen_dall_e_3(prompt):
    """
    Genera una imagen usando DALL-E 3, la descarga y la sube a S3.
    Args:
        prompt (str): Descripción de la imagen que se quiere generar.
    Returns:
        str: Path de la imagen en S3.
    """
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "size": "1024x1024",
        "quality": "standard",
        "n": 1,
    }
    try:
        # Generar la imagen
        response = requests.post(
            f"{os.getenv('OPENAI_API_URL')}images/generations",
            headers=get_cabeceros_openai(),
            json=data
        )
        if response.status_code != 200:
            abort(HTTPStatus.BAD_REQUEST, description=f"Error al generar la imagen: {response.text}")

        response_json = response.json()
        imagen_url = response_json["data"][0]["url"]

        # Descargar la imagen usando pycurl
        imagen_content = descargar_imagen_con_curl(imagen_url)

        # Subir a S3
        s3_client = get_conection()
        bucket_name = os.getenv('AWS_BUCKET')
        s3_key = f"dalle_{int(time.time())}.png"  # Usa un nombre único

        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=imagen_content,
            ContentType='image/png'
        )

        # Devolver el path en S3
        return f"{s3_key}"

    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.NOT_FOUND)
    except Exception as e:
        #return f"error={e}"
        abort(HTTPStatus.NOT_FOUND)


def transcribir_audio_openai(audio_file_path):
    """
    Transcribe un archivo de audio local a texto usando la API de Whisper de OpenAI.
    
    Args:
        audio_file_path (str): Ruta local al archivo de audio (mp3, wav, etc.)
        
    Returns:
        str: Texto transcrito del audio
    """
    try:
        # Verificar que el archivo existe
        if not os.path.exists(audio_file_path):
            abort(HTTPStatus.BAD_REQUEST, description="El archivo de audio no existe")
        
        # Verificar tamaño del archivo (límite de Whisper: 25MB)
        file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # MB
        if file_size > 25:
            abort(HTTPStatus.BAD_REQUEST, description="El archivo es demasiado grande (máximo 25MB)")
        
        # Preparar la solicitud para la API de Whisper
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'file': (os.path.basename(audio_file_path), audio_file, 'audio/mpeg'),
                'model': (None, 'whisper-1'),
                'response_format': (None, 'text'),
                'language': (None, 'es')  # Opcional: especificar español
            }
            
            response = requests.post(
                f"{os.getenv('OPENAI_API_URL')}audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
                },
                files=files
            )
        
        if response.status_code == 200:
            return response.text
        else:
            abort(HTTPStatus.BAD_REQUEST, description=f"Error en la transcripción: {response.text}")
            
    except Exception as e:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Error interno: {str(e)}")


def get_chat_con_historial_openai(mensajes_historial):
    """
    Realiza una consulta a OpenAI con historial de conversación completo
    mensajes_historial: Lista de mensajes con formato [{"role": "user/assistant", "content": "mensaje"}, ...]
    """
    
    data = {
        "model": "gpt-4o-mini",
        "messages": mensajes_historial,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            f"{os.getenv('OPENAI_API_URL')}chat/completions",
            headers=get_cabeceros_openai(),
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            response_json = response.json()
            return response_json["choices"][0]["message"]["content"]
        else:
            print(f"Error en OpenAI API: {response.status_code} - {response.text}")
            abort(HTTPStatus.NOT_FOUND)
            
    except Exception as e:
        print(f"Error en conexión con OpenAI: {e}")
        abort(HTTPStatus.NOT_FOUND)