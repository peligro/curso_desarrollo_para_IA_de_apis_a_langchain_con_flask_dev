from flask import abort
from http import HTTPStatus
import requests
import PyPDF2
from dotenv import load_dotenv
import os 

load_dotenv()


def extraer_texto_pdf(ruta_pdf):
    """Extrae todo el texto del PDF"""
    texto = ""
    try:
        with open(ruta_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                texto += page.extract_text() + "\n"
        return texto
    except Exception as e:
        print(f"Error leyendo PDF: {e}")
        return ""


def retornarContecto():
    contexto_pdf = extraer_texto_pdf("static/pdf/manual_atencion_cliente.pdf")
    return contexto_pdf


def get_consulta_rag_mistral(pregunta, contexto_pdf):
    """
    Consulta simple RAG usando Mistral con contexto del PDF
    """
    prompt = f"""
    Eres un asistente virtual de atención al cliente. 
    Basa tu respuesta EXCLUSIVAMENTE en la siguiente información del manual:

    INFORMACIÓN DEL MANUAL DE ATENCIÓN AL CLIENTE:
    {contexto_pdf}

    PREGUNTA DEL CLIENTE:
    {pregunta}

    INSTRUCCIONES:
    - Responde de manera clara y profesional usando SOLO la información del manual
    - Si la información no está en el manual, di "No encontré información específica sobre esto en el manual"
    - Mantén un tono amable y útil
    - Sé conciso (máximo 150 palabras)
    - Responde en español
    """
    
    data = {
        "model": "mistral-small",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }
    
    response = requests.post(
        f"{os.getenv('MISTRAL_BASE_URL')}chat/completions",
        headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}"
                },
        json=data
    )
    
    if response.status_code == 200:
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"]
    else:
        return f"Error al consultar la API: {response.status_code}"
    

def get_consulta_rag_ollama(pregunta, contexto_pdf):
        """
        Consulta simple RAG usando Ollama con contexto del PDF
        """
        prompt = f"""
        Eres un asistente virtual de atención al cliente. 
        Basa tu respuesta EXCLUSIVAMENTE en la siguiente información del manual:

        INFORMACIÓN DEL MANUAL DE ATENCIÓN AL CLIENTE:
        {contexto_pdf}

        PREGUNTA DEL CLIENTE:
        {pregunta}

        INSTRUCCIONES:
        - Responde de manera clara y profesional usando SOLO la información del manual
        - Si la información no está en el manual, di "No encontré información específica sobre esto en el manual"
        - Mantén un tono amable y útil
        - Sé conciso (máximo 150 palabras)
        - Responde en español
        - No agregues explicaciones adicionales ni comentarios sobre el formato
        """
        
        data = {
            "model": "gemma:2b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{os.getenv('OLLAMA_BASE_URL')}api/chat",
                headers={
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"Error al consultar Ollama API: {response.status_code}"
                
        except Exception as e:
            return f"Error de conexión con Ollama: {str(e)}"


def get_consulta_rag_gemini(pregunta, contexto_pdf):
    """
    Consulta simple RAG usando Gemini con contexto del PDF
    """
    prompt = f"""
    Eres un asistente virtual de atención al cliente. 
    Basa tu respuesta EXCLUSIVAMENTE en la siguiente información del manual:

    INFORMACIÓN DEL MANUAL DE ATENCIÓN AL CLIENTE:
    {contexto_pdf}

    PREGUNTA DEL CLIENTE:
    {pregunta}

    INSTRUCCIONES:
    - Responde de manera clara y profesional usando SOLO la información del manual
    - Si la información no está en el manual, di "No encontré información específica sobre esto en el manual"
    - Mantén un tono amable y útil
    - Sé conciso (máximo 150 palabras)
    - Responde en español
    - No agregues explicaciones adicionales ni comentarios sobre el formato
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
            'temperature': 0.3,
            'maxOutputTokens': 500,
        }
    }

    try:
        response = requests.post(
            f"{os.getenv('GEMINI_BASE_URL')}models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers={
                "Content-Type": "application/json"
            },
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        respuesta_ia = data['candidates'][0]['content']['parts'][0]['text']
        return respuesta_ia
        
    except requests.exceptions.RequestException as e:
        return f"Error al consultar Gemini API: {str(e)}"
    

def get_consulta_rag_claude(pregunta, contexto_pdf):
    """
    Consulta simple RAG usando Claude con contexto del PDF
    """
    prompt = f"""
    Eres un asistente virtual de atención al cliente. 
    Basa tu respuesta EXCLUSIVAMENTE en la siguiente información del manual:

    INFORMACIÓN DEL MANUAL DE ATENCIÓN AL CLIENTE:
    {contexto_pdf}

    PREGUNTA DEL CLIENTE:
    {pregunta}

    INSTRUCCIONES:
    - Responde de manera clara y profesional usando SOLO la información del manual
    - Si la información no está en el manual, di "No encontré información específica sobre esto en el manual"
    - Mantén un tono amable y útil
    - Sé conciso (máximo 150 palabras)
    - Responde en español
    - No agregues explicaciones adicionales ni comentarios sobre el formato
    """
    
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 500,
        "temperature": 0.3,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{os.getenv('CLAUDE_BASE_URL')}messages",
            headers={
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
                "x-api-key": f"{os.getenv('CLAUDE_API_KEY')}"
            },
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            response_json = response.json()
            return response_json["content"][0]["text"]
        else:
            return f"Error al consultar Claude API: {response.status_code}"
            
    except Exception as e:
        return f"Error de conexión con Claude: {str(e)}"
    

def get_consulta_rag_deepseek(pregunta, contexto_pdf):
    """
    Consulta simple RAG usando DeepSeek con contexto del PDF
    """
    prompt = f"""
    Eres un asistente virtual de atención al cliente. 
    Basa tu respuesta EXCLUSIVAMENTE en la siguiente información del manual:

    INFORMACIÓN DEL MANUAL DE ATENCIÓN AL CLIENTE:
    {contexto_pdf}

    PREGUNTA DEL CLIENTE:
    {pregunta}

    INSTRUCCIONES:
    - Responde de manera clara y profesional usando SOLO la información del manual
    - Si la información no está en el manual, di "No encontré información específica sobre esto en el manual"
    - Mantén un tono amable y útil
    - Sé conciso (máximo 150 palabras)
    - Responde en español
    - No agregues explicaciones adicionales ni comentarios sobre el formato
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            f"{os.getenv('DEEPSEEK_API_URL')}chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"
            },
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            response_json = response.json()
            return response_json["choices"][0]["message"]["content"]
        else:
            return f"Error al consultar DeepSeek API: {response.status_code}"
            
    except Exception as e:
        return f"Error de conexión con DeepSeek: {str(e)}"


def get_consulta_rag_openai(pregunta, contexto_pdf):
    """
    Consulta simple RAG usando OpenAI con contexto del PDF
    """
    prompt = f"""
    Eres un asistente virtual de atención al cliente. 
    Basa tu respuesta EXCLUSIVAMENTE en la siguiente información del manual:

    INFORMACIÓN DEL MANUAL DE ATENCIÓN AL CLIENTE:
    {contexto_pdf}

    PREGUNTA DEL CLIENTE:
    {pregunta}

    INSTRUCCIONES:
    - Responde de manera clara y profesional usando SOLO la información del manual
    - Si la información no está en el manual, di "No encontré información específica sobre esto en el manual"
    - Mantén un tono amable y útil
    - Sé conciso (máximo 150 palabras)
    - Responde en español
    - No agregues explicaciones adicionales ni comentarios sobre el formato
    """
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            f"{os.getenv('OPENAI_API_URL')}chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
            },
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            response_json = response.json()
            return response_json["choices"][0]["message"]["content"]
        else:
            return f"Error al consultar OpenAI API: {response.status_code}"
            
    except Exception as e:
        return f"Error de conexión con OpenAI: {str(e)}"


