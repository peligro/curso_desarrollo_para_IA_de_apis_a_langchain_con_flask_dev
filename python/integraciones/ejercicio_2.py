import os
import requests
import json
import time
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class RecetasRAG:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_name = os.getenv('PINECONE_API_INDEX')
        self.setup_pinecone()
    
    def setup_pinecone(self):
        """Conecta con el índice de Pinecone"""
        try:
            if self.index_name not in self.pc.list_indexes().names():
                print(f"❌ El índice '{self.index_name}' no existe.")
                return False
            
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Conectado al índice: {self.index_name}")
            return True
        except Exception as e:
            print(f"❌ Error conectando a Pinecone: {e}")
            return False
    
    def limpiar_y_cargar_desde_json(self, ruta_archivo=None):
        """Borra TODAS las recetas y carga desde JSON - Ideal para datos actualizados"""
        if ruta_archivo is None:
            ruta_archivo = "static/json/recetas.json"
        
        try:
            print("🔄 Iniciando refresh completo de la base de datos...")
            
            # 1. Cargar el JSON actualizado primero
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ruta_completa = os.path.join(base_dir, ruta_archivo)
            
            print(f"📁 Cargando recetas desde: {ruta_completa}")
            
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                recetas_actualizadas = json.load(f)
            
            print(f"📖 JSON cargado con {len(recetas_actualizadas)} recetas actualizadas")
            
            # 2. Borrar TODO el contenido del índice
            print("🗑️ Eliminando todas las recetas existentes...")
            self.index.delete(delete_all=True)
            
            # Pequeña pausa para asegurar que la eliminación se procese
            time.sleep(2)
            
            # 3. Cargar las recetas actualizadas
            vectors = []
            for receta in recetas_actualizadas:
                # Crear texto para embedding
                texto = f"{receta['nombre']} {receta['ingredientes']} {receta['categoria']}"
                embedding = self.embedder.encode(texto).tolist()
                
                vectors.append({
                    "id": receta["id"],
                    "values": embedding,
                    "metadata": receta
                })
            
            # 4. Insertar en Pinecone
            self.index.upsert(vectors=vectors)
            
            # 5. Verificar carga exitosa
            stats_final = self.index.describe_index_stats()
            
            mensaje = f"🔄 Base de datos actualizada: {len(recetas_actualizadas)} recetas cargadas desde JSON"
            print(mensaje)
            return mensaje
            
        except FileNotFoundError:
            error_msg = f"❌ Archivo no encontrado: {ruta_archivo}"
            print(error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = f"❌ Error decodificando JSON: {e}"
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ Error en refresh completo: {e}"
            print(error_msg)
            return error_msg
    
    def buscar_recetas_similares(self, consulta, top_k=5):
        """Busca recetas similares usando embeddings"""
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedder.encode(consulta).tolist()
            
            # Buscar en Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            recetas_encontradas = []
            for match in results.matches:
                receta = match.metadata
                receta['score'] = match.score
                recetas_encontradas.append(receta)
            
            return recetas_encontradas
        except Exception as e:
            print(f"❌ Error buscando recetas: {e}")
            return []
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas de la base de datos"""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_recetas': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness
            }
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return None

# Funciones para las IAs (se mantienen igual)
def buscar_recetas_ollama(consulta, recetas_contexto):
    prompt = f"""
    Eres un chef asistente experto. Basándote EXCLUSIVAMENTE en estas recetas encontradas:

    {json.dumps(recetas_contexto, indent=2, ensure_ascii=False)}

    Responde a esta consulta del usuario: "{consulta}"

    INSTRUCCIONES:
    - Si las recetas encontradas son relevantes, recomienda las más apropiadas explicando por qué
    - Si no hay recetas relevantes, sugiere alternativas basadas en tu conocimiento culinario
    - Incluye tiempos de preparación y dificultad cuando sea relevante
    - Responde en español de manera útil, amable y profesional
    - Sé conciso pero informativo
    """
    
    data = {
        "model": "gemma:2b",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{os.getenv('OLLAMA_BASE_URL')}api/chat",
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Error en la búsqueda con Ollama: {response.status_code}"
    except Exception as e:
        return f"Error de conexión con Ollama: {str(e)}"

def buscar_recetas_mistral(consulta, recetas_contexto):
    prompt = f"""
    Eres un chef asistente. Basándote en estas recetas encontradas:

    {json.dumps(recetas_contexto, indent=2, ensure_ascii=False)}

    Responde a: "{consulta}"

    INSTRUCCIONES:
    - Recomienda recetas relevantes de la lista
    - Si no hay coincidencias, sugiere alternativas
    - Incluye información práctica como tiempo y dificultad
    - Responde en español de forma clara y profesional
    """
    
    data = {
        "model": "mistral-small",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            f"{os.getenv('MISTRAL_BASE_URL')}chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}"},
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error en la búsqueda con Mistral: {response.status_code}"
    except Exception as e:
        return f"Error de conexión con Mistral: {str(e)}"

def buscar_recetas_gemini(consulta, recetas_contexto):
    prompt = f"""
    Como chef asistente, usa estas recetas:

    {json.dumps(recetas_contexto, indent=2, ensure_ascii=False)}

    Para responder: "{consulta}"

    Responde en español, sé útil y profesional.
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
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error de conexión con Gemini: {str(e)}"

def buscar_recetas_claude(consulta, recetas_contexto):
    prompt = f"""
    Eres un chef asistente. Basándote en estas recetas:

    {json.dumps(recetas_contexto, indent=2, ensure_ascii=False)}

    Responde a: "{consulta}"

    Responde en español de manera útil.
    """
    
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 500,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
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
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            return f"Error con Claude: {response.status_code}"
    except Exception as e:
        return f"Error de conexión con Claude: {str(e)}"

def buscar_recetas_deepseek(consulta, recetas_contexto):
    prompt = f"""
    Como chef asistente, usa estas recetas:

    {json.dumps(recetas_contexto, indent=2, ensure_ascii=False)}

    Para: "{consulta}"

    Responde en español.
    """
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
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
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error con DeepSeek: {response.status_code}"
    except Exception as e:
        return f"Error de conexión con DeepSeek: {str(e)}"

def buscar_recetas_openai(consulta, recetas_contexto):
    prompt = f"""
    Eres un chef asistente. Basándote en:

    {json.dumps(recetas_contexto, indent=2, ensure_ascii=False)}

    Responde: "{consulta}"

    Responde en español.
    """
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
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
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error con OpenAI: {response.status_code}"
    except Exception as e:
        return f"Error de conexión con OpenAI: {str(e)}"

# Función principal SIMPLIFICADA
def get_recetas_rag(ia, consulta):
    """Función principal para buscar recetas con RAG"""
    rag_recetas = RecetasRAG()
    
    # Verificar conexión
    if not hasattr(rag_recetas, 'index') or rag_recetas.index is None:
        return "Error: No se pudo conectar a la base de datos de recetas."
    
    # Verificar si hay datos
    try:
        stats = rag_recetas.obtener_estadisticas()
        if stats and stats['total_recetas'] == 0:
            return "La base de datos está vacía. Por favor, actualiza los datos desde el botón 'Actualizar Base de Datos'."
        else:
            print(f"📊 Buscando en {stats['total_recetas']} recetas...")
    except Exception as e:
        return "Error accediendo a la base de datos."
    
    # Buscar recetas similares
    recetas_encontradas = rag_recetas.buscar_recetas_similares(consulta)
    
    if not recetas_encontradas:
        return "No encontré recetas similares en la base de datos. Intenta con otros ingredientes o categorías."
    
    # Usar la IA seleccionada
    if ia == "Ollama":
        return buscar_recetas_ollama(consulta, recetas_encontradas)
    elif ia == "Mistral":
        return buscar_recetas_mistral(consulta, recetas_encontradas)
    elif ia == "Gemini":
        return buscar_recetas_gemini(consulta, recetas_encontradas)
    elif ia == "Claude":
        return buscar_recetas_claude(consulta, recetas_encontradas)
    elif ia == "Deepseek":
        return buscar_recetas_deepseek(consulta, recetas_encontradas)
    elif ia == "OpenAI":
        return buscar_recetas_openai(consulta, recetas_encontradas)
    
    return "IA no implementada aún"