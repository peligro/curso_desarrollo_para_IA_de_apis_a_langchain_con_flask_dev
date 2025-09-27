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
    response = requests.post(f"{os.getenv('MISTRAL_BASE_URL')}chat/completions", headers=get_cabeceros_mistral(), json=data)
    if response.status_code == 200:
        response_json = response.json()
        # Devolver directamente el contenido del mensaje
        return response_json["choices"][0]["message"]["content"]
    else:
        print(f"Error en la solicitud: {response.status_code}")
        print(response.text)
