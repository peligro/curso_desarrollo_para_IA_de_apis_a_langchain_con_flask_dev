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
    - no envuelvas la consulta en ```sql ```
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


def get_consulta_imagen_gemini(pregunta, url_imagen):
    
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

    payload = {
        'contents': [
            {
                'parts': [
                    {'text': prompt_optimizado},
                    {
                        'inline_data': {
                            'mime_type': content_type,
                            'data': imagen_base64
                        }
                    }
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
        response.raise_for_status()

        data = response.json()
        
        # Verificar si hay bloqueos de seguridad en la respuesta
        if 'promptFeedback' in data and 'blockReason' in data['promptFeedback']:
            return "La imagen no puede ser analizada debido a restricciones de contenido."
            
        respuesta_ia = data['candidates'][0]['content']['parts'][0]['text']
        return respuesta_ia
        
    except requests.exceptions.RequestException as e:
        abort(HTTPStatus.NOT_FOUND)


def transcribir_audio_gemini(audio_file_path):
    """
    Transcribe un archivo de audio a texto usando Google Gemini.
    
    Args:
        audio_file_path (str): Ruta local al archivo de audio (mp3, wav, etc.)
        
    Returns:
        str: Texto transcrito del audio
    """
    try:
        # Verificar que el archivo existe
        if not os.path.exists(audio_file_path):
            abort(HTTPStatus.BAD_REQUEST, description="El archivo de audio no existe")
        
        # Verificar tamaño del archivo (Gemini tiene límites)
        file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # MB
        if file_size > 20:
            abort(HTTPStatus.BAD_REQUEST, description="El archivo es demasiado grande (máximo 20MB)")
        
        # Determinar el formato del archivo
        file_extension = audio_file_path.lower().split('.')[-1]
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac'
        }
        mime_type = mime_types.get(file_extension, 'audio/mpeg')
        
        # Leer el archivo de audio y convertirlo a base64
        with open(audio_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Preparar el payload para Gemini
        payload = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': "Transcribe este audio a texto exactamente como se escucha. Devuelve solo la transcripción sin comentarios adicionales, títulos o explicaciones."
                        },
                        {
                            'inline_data': {
                                'mime_type': mime_type,
                                'data': audio_base64
                            }
                        }
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.1,  # Temperatura baja para mayor precisión
                'maxOutputTokens': 2000,  # Suficiente para transcripciones largas
            }
        }
        
        # Realizar la solicitud a Gemini
        response = requests.post(
            f"{os.getenv('GEMINI_BASE_URL')}models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers=get_cabeceros(),
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar si hay bloqueos de seguridad
            if 'promptFeedback' in data and 'blockReason' in data['promptFeedback']:
                abort(HTTPStatus.BAD_REQUEST, description="El audio no puede ser procesado debido a restricciones de contenido")
            
            # Extraer la transcripción
            if 'candidates' in data and len(data['candidates']) > 0:
                transcription = data['candidates'][0]['content']['parts'][0]['text']
                return transcription.strip()
            else:
                abort(HTTPStatus.BAD_REQUEST, description="Gemini no devolvió una transcripción válida")
        else:
            error_msg = f"Error en la transcripción: {response.status_code} - {response.text}"
            abort(HTTPStatus.BAD_REQUEST, description=error_msg)
            
    except Exception as e:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Error interno: {str(e)}")


def analizar_video_gemini(video_file_path, pregunta_personalizada=None):
    """
    Analiza un video MP4 usando Google Gemini.
    
    Args:
        video_file_path (str): Ruta local al archivo de video MP4
        pregunta_personalizada (str): Pregunta específica sobre el video
        
    Returns:
        str: Análisis del contenido del video
    """
    try:
        # Verificar que el archivo existe
        if not os.path.exists(video_file_path):
            abort(HTTPStatus.BAD_REQUEST, description="El archivo de video no existe")
        
        # Verificar tamaño del archivo (límite de Gemini: ~20MB)
        file_size = os.path.getsize(video_file_path) / (1024 * 1024)
        if file_size > 20:
            abort(HTTPStatus.BAD_REQUEST, description="El video es demasiado grande (máximo 20MB)")
        
        # Verificar duración (límite aproximado: 2 minutos)
        # Podrías agregar una verificación de duración con librerías como moviepy
        
        # Leer el archivo de video y convertirlo a base64
        with open(video_file_path, 'rb') as video_file:
            video_data = video_file.read()
            video_base64 = base64.b64encode(video_data).decode('utf-8')
        
        # Construir el prompt
        if pregunta_personalizada:
            prompt_text = pregunta_personalizada
        else:
            prompt_text = """
            Analiza este video y describe:
            1. Qué se ve en el video (escenas, personas, objetos, acciones)
            2. El contexto o situación
            3. Elementos importantes o destacados
            
            Sé descriptivo y objetivo.
            """
        
        # Preparar el payload para Gemini
        payload = {
            'contents': [
                {
                    'parts': [
                        {'text': prompt_text},
                        {
                            'inline_data': {
                                'mime_type': 'video/mp4',
                                'data': video_base64
                            }
                        }
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.2,
                'maxOutputTokens': 1000,
            }
        }
        
        # Realizar la solicitud a Gemini
        response = requests.post(
            f"{os.getenv('GEMINI_BASE_URL')}models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers=get_cabeceros(),
            json=payload,
            timeout=120  # Timeout más largo para videos
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar bloqueos de seguridad
            if 'promptFeedback' in data and 'blockReason' in data['promptFeedback']:
                abort(HTTPStatus.BAD_REQUEST, description="El video no puede ser analizado debido a restricciones de contenido")
            
            # Extraer el análisis
            if 'candidates' in data and len(data['candidates']) > 0:
                analisis = data['candidates'][0]['content']['parts'][0]['text']
                return analisis.strip()
            else:
                abort(HTTPStatus.BAD_REQUEST, description="Gemini no devolvió un análisis válido")
        else:
            error_msg = f"Error al analizar el video: {response.status_code} - {response.text}"
            abort(HTTPStatus.BAD_REQUEST, description=error_msg)
            
    except Exception as e:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=f"Error interno: {str(e)}")