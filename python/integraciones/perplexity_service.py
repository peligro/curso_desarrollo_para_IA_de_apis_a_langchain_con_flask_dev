from flask import abort
from http import HTTPStatus
import requests
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def get_cabeceros_perplexity():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"
    }

def get_busqueda_basica_perplexity(pregunta ):
    """
    Realiza una búsqueda básica con Perplexity AI y devuelve respuesta con fuentes
    
     
    """
    
    data = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": pregunta
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.2,
        "return_citations": True,  # Para obtener fuentes
        "stream": False
    }
    
    try:
        # URL correcta de Perplexity API
        response = requests.post(
            f"{os.getenv('PERPLEXITY_BASE_URL')}chat/completions",  # URL directa para evitar problemas
            headers=get_cabeceros_perplexity(),
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            response_json = response.json()
            
            # Extraer la respuesta principal
            respuesta = response_json["choices"][0]["message"]["content"]
            
            # Extraer citas/fuentes si están disponibles
            citas = []
            if 'citations' in response_json:
                citas = response_json['citations']
            
            return {
                "respuesta": respuesta,
                "citas": citas,
                "modelo_usado": "sonar"
            }
        else:
            #print(f"Error en Perplexity API: {response.status_code} - {response.text}")
            # Mejor manejo de errores
            error_msg = f"Error {response.status_code}: {response.text}"
            return {
                "respuesta": f"Error en la búsqueda: {error_msg}",
                "citas": [],
                "modelo_usado": "sonar",
                "error": True
            }
            
    except Exception as e:
        #print(f"Error en conexión con Perplexity: {e}")
        return {
            "respuesta": f"Error de conexión: {str(e)}",
            "citas": [],
            "modelo_usado": "sonar",
            "error": True
        }