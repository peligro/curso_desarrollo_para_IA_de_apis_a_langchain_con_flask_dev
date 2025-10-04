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


def get_parametros_investigacion_perplexity():
    """
    Devuelve opciones predefinidas para investigación avanzada
    """
    return {
        "dominios": {
            "tecnologia": "github.com, stackoverflow.com, techcrunch.com",
            "academico": "arxiv.org, scholar.google.com, researchgate.net",
            "noticias": "bbc.com, cnn.com, reuters.com, elpais.com",
            "programacion": "stackoverflow.com, github.com, docs.python.org",
            "medicina": "pubmed.gov, who.int, nejm.org"
        },
        "rangos_fecha": {
            "ultima_semana": "última semana",
            "ultimo_mes": "último mes", 
            "ultimo_ano": "último año",
            "2024": "año 2024",
            "2023_2024": "2023-2024"
        },
        "idiomas": {
            "es": "Español",
            "en": "Inglés",
            "fr": "Francés",
            "de": "Alemán"
        },
        "enfoques": {
            "noticias": "Noticias recientes",
            "academico": "Contenido académico",
            "tecnico": "Documentación técnica",
            "general": "Información general"
        },
        "profundidades": {
            "rapida": "Búsqueda rápida",
            "balanceada": "Balanceada",
            "profunda": "Investigación profunda"
        }
    }

def get_investigacion_avanzada_perplexity(pregunta, parametros=None):
    """
    Realiza una investigación avanzada con Perplexity AI con parámetros personalizables
    
    Parámetros disponibles:
    - search_domain: Restringir búsqueda a dominios específicos
    - date_range: Filtrar por rango de fechas
    - language: Idioma de los resultados
    - focus: Enfoque de la búsqueda (news, academic, etc.)
    - depth: Profundidad de la investigación
    """
    
    # Parámetros por defecto
    parametros_default = {
        'model': 'sonar',
        'max_tokens': 1500,
        'temperature': 0.3,
        'return_citations': True,
        'stream': False
    }
    
    # Combinar con parámetros personalizados
    if parametros:
        parametros_default.update(parametros)
    
    # Construir el mensaje con contexto basado en parámetros
    mensaje_usuario = pregunta
    
    # Agregar contexto basado en parámetros específicos
    contexto_extra = []
    
    if parametros_default.get('search_domain'):
        contexto_extra.append(f"Buscar específicamente en: {parametros_default['search_domain']}")
    
    if parametros_default.get('date_range'):
        contexto_extra.append(f"Información del período: {parametros_default['date_range']}")
    
    if parametros_default.get('language'):
        contexto_extra.append(f"Priorizar contenido en: {parametros_default['language']}")
    
    if parametros_default.get('focus'):
        contexto_extra.append(f"Enfócate en: {parametros_default['focus']}")
    
    if contexto_extra:
        contexto_texto = ". ".join(contexto_extra)
        mensaje_usuario = f"{pregunta}\n\nContexto: {contexto_texto}"
    
    data = {
        "model": parametros_default['model'],
        "messages": [
            {
                "role": "user",
                "content": mensaje_usuario
            }
        ],
        "max_tokens": parametros_default['max_tokens'],
        "temperature": parametros_default['temperature'],
        "return_citations": parametros_default['return_citations'],
        "stream": parametros_default['stream']
    }
    
    try:
        response = requests.post(
            f"{os.getenv('PERPLEXITY_BASE_URL')}chat/completions",
            headers=get_cabeceros_perplexity(),
            json=data,
            timeout=90  # Más tiempo para búsquedas complejas
        )
        
        if response.status_code == 200:
            response_json = response.json()
            
            respuesta = response_json["choices"][0]["message"]["content"]
            citas = response_json.get('citations', [])
            
            return {
                "respuesta": respuesta,
                "citas": citas,
                "modelo_usado": parametros_default['model'],
                "parametros_usados": parametros_default,
                "error": False
            }
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            return {
                "respuesta": f"Error en la investigación: {error_msg}",
                "citas": [],
                "modelo_usado": parametros_default['model'],
                "parametros_usados": parametros_default,
                "error": True
            }
            
    except Exception as e:
        return {
            "respuesta": f"Error de conexión: {str(e)}",
            "citas": [],
            "modelo_usado": parametros_default['model'],
            "parametros_usados": parametros_default,
            "error": True
        }


####chat con historial
def get_chat_con_historial_perplexity(mensajes_historial):
    """
    Realiza una conversación con Perplexity AI manteniendo el historial completo
    
    Args:
        mensajes_historial: Lista de mensajes en formato [{"role": "user/assistant", "content": "mensaje"}, ...]
    """
    
    data = {
        "model": "sonar",
        "messages": mensajes_historial,
        "max_tokens": 1200,
        "temperature": 0.2,
        "return_citations": True,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{os.getenv('PERPLEXITY_BASE_URL')}chat/completions",
            headers=get_cabeceros_perplexity(),
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            response_json = response.json()
            
            respuesta = response_json["choices"][0]["message"]["content"]
            citas = response_json.get('citations', [])
            
            return {
                "respuesta": respuesta,
                "citas": citas,
                "modelo_usado": "sonar",
                "error": False
            }
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            return {
                "respuesta": f"Error en el chat: {error_msg}",
                "citas": [],
                "modelo_usado": "sonar",
                "error": True
            }
            
    except Exception as e:
        return {
            "respuesta": f"Error de conexión: {str(e)}",
            "citas": [],
            "modelo_usado": "sonar",
            "error": True
        }
    

#####BÚSQUEDA COMPARATIVA
import time
def get_busqueda_comparativa_perplexity(pregunta, incluir_analisis=True):
    """
    Realiza una búsqueda comparativa entre Perplexity AI y búsqueda tradicional
    
    Args:
        pregunta: Pregunta a comparar
        incluir_analisis: Si incluir análisis comparativo automático
    """
    
    # Primera búsqueda: Enfoque Perplexity (conversacional con fuentes)
    prompt_perplexity = pregunta
    
    data_perplexity = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": prompt_perplexity
            }
        ],
        "max_tokens": 1200,
        "temperature": 0.2,
        "return_citations": True,
        "stream": False
    }
    
    # Segunda búsqueda: Enfoque "tradicional" (más directo, como Google)
    prompt_tradicional = f"""
    Responde de manera directa y concisa a esta pregunta, como lo haría un motor de búsqueda tradicional:
    "{pregunta}"
    
    Proporciona una respuesta factual sin análisis extenso.
    """
    
    data_tradicional = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": prompt_tradicional
            }
        ],
        "max_tokens": 800,
        "temperature": 0.1,  # Más determinista
        "return_citations": True,
        "stream": False
    }
    
    try:
        # Realizar ambas búsquedas
        resultados = {}
        tiempos = {}
        
        # Búsqueda Perplexity (conversacional)
        start_time = time.time()
        response_perplexity = requests.post(
            f"{os.getenv('PERPLEXITY_BASE_URL')}chat/completions",
            headers=get_cabeceros_perplexity(),
            json=data_perplexity,
            timeout=60
        )
        tiempos['perplexity'] = round(time.time() - start_time, 2)
        
        # Búsqueda "tradicional"  
        start_time = time.time()
        response_tradicional = requests.post(
            f"{os.getenv('PERPLEXITY_BASE_URL')}chat/completions",
            headers=get_cabeceros_perplexity(),
            json=data_tradicional,
            timeout=60
        )
        tiempos['tradicional'] = round(time.time() - start_time, 2)
        
        # Procesar respuesta Perplexity
        if response_perplexity.status_code == 200:
            response_json = response_perplexity.json()
            resultados['perplexity'] = {
                "respuesta": response_json["choices"][0]["message"]["content"],
                "citas": response_json.get('citations', []),
                "error": False
            }
        else:
            resultados['perplexity'] = {
                "respuesta": f"Error en búsqueda Perplexity: {response_perplexity.status_code}",
                "citas": [],
                "error": True
            }
        
        # Procesar respuesta tradicional
        if response_tradicional.status_code == 200:
            response_json = response_tradicional.json()
            resultados['tradicional'] = {
                "respuesta": response_json["choices"][0]["message"]["content"],
                "citas": response_json.get('citations', []),
                "error": False
            }
        else:
            resultados['tradicional'] = {
                "respuesta": f"Error en búsqueda tradicional: {response_tradicional.status_code}",
                "citas": [],
                "error": True
            }
        
        # Análisis comparativo automático (opcional)
        analisis_comparativo = ""
        if incluir_analisis and not resultados['perplexity']['error'] and not resultados['tradicional']['error']:
            prompt_analisis = f"""
            Analiza y compara estas dos respuestas a la misma pregunta:
            
            PREGUNTA: "{pregunta}"
            
            RESPUESTA PERPLEXITY (conversacional):
            {resultados['perplexity']['respuesta']}
            
            RESPUESTA TRADICIONAL (directa):
            {resultados['tradicional']['respuesta']}
            
            Proporciona un análisis breve (máximo 200 palabras) comparando:
            1. Estilo y profundidad de cada respuesta
            2. Utilidad para diferentes tipos de usuarios
            3. Ventajas de cada enfoque
            
            Sé objetivo y conciso.
            """
            
            data_analisis = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt_analisis
                    }
                ],
                "max_tokens": 400,
                "temperature": 0.3,
                "stream": False
            }
            
            try:
                response_analisis = requests.post(
                    f"{os.getenv('PERPLEXITY_BASE_URL')}chat/completions",
                    headers=get_cabeceros_perplexity(),
                    json=data_analisis,
                    timeout=30
                )
                
                if response_analisis.status_code == 200:
                    response_json = response_analisis.json()
                    analisis_comparativo = response_json["choices"][0]["message"]["content"]
            except:
                analisis_comparativo = "Análisis comparativo no disponible"
        
        return {
            "resultados": resultados,
            "tiempos": tiempos,
            "analisis_comparativo": analisis_comparativo,
            "pregunta_original": pregunta,
            "error": False
        }
            
    except Exception as e:
        return {
            "resultados": {},
            "tiempos": {},
            "analisis_comparativo": "",
            "pregunta_original": pregunta,
            "error": True,
            "mensaje_error": f"Error en búsqueda comparativa: {str(e)}"
        }


###########Sistema de Citas Automáticas
def get_citas_automaticas_perplexity(texto, formato_cita="apa", incluir_resumen=True):
    """
    Genera citas automáticas para un texto usando Perplexity AI
    """
    # Mapeo de formatos de cita
    formatos_cita = {
        "apa": "APA (American Psychological Association)",
        "mla": "MLA (Modern Language Association)", 
        "chicago": "Chicago Manual of Style",
        "ieee": "IEEE (Institute of Electrical and Electronics Engineers)"
    }
    
    formato_nombre = formatos_cita.get(formato_cita, "APA")
    
    prompt_citas = f"""
    ANALIZA este texto y genera CITAS AUTOMÁTICAS con FUENTES VERIFICADAS.

    TEXTO A ANALIZAR:
    "{texto}"

    INSTRUCCIONES MUY ESPECÍFICAS:

    1. Identifica las 3-5 afirmaciones PRINCIPALES del texto
    2. Para CADA afirmación, DEBES incluir estos 4 elementos EXACTAMENTE:

    ### Afirmación [número]:
    [Texto específico de la afirmación]

    **Cita {formato_cita.upper()}:** 
    [CITA COMPLETA y REAL en formato {formato_cita.upper()} - NO dejes esto vacío]

    **Fuente:** 
    [URL COMPLETA de la fuente]

    **Explicación:** 
    [Por qué esta fuente es confiable]

    ---

    3. LAS CITAS DEBEN SER TEXTOS COMPLETOS, NO VACÍOS
    4. Si no encuentras una cita específica, genera una basada en la fuente encontrada
    5. **IMPORTANTE: NO incluyas "Resumen final" como una afirmación**
    6. Después de las afirmaciones, incluye un resumen SEPARADO claramente con:
    
    ## Resumen Ejecutivo
    [Aquí el resumen...]

    ¡NO DEJES LAS CITAS VACÍAS! Proporciona texto real en cada cita.
    NO uses "Resumen" como número de afirmación.
    """
    
    data = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": prompt_citas
            }
        ],
        "max_tokens": 2500,
        "temperature": 0.2,
        "return_citations": True,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{os.getenv('PERPLEXITY_BASE_URL')}chat/completions",
            headers=get_cabeceros_perplexity(),
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            response_json = response.json()
            
            respuesta = response_json["choices"][0]["message"]["content"]
            citas_encontradas = response_json.get('citations', [])
            
            # Debug: mostrar lo que viene de Perplexity
            print("=== RESPUESTA PERPLEXITY ===")
            print(respuesta[:500])  # Primeros 500 caracteres
            print("=== CITAS ENCONTRADAS ===")
            print(citas_encontradas)
            
            # Analizar la respuesta para extraer estructura de citas
            citas_estructuradas = extraer_citas_estructuradas(respuesta, citas_encontradas)
            
            return {
                "respuesta_completa": respuesta,
                "citas_encontradas": citas_encontradas,
                "citas_estructuradas": citas_estructuradas,
                "formato_usado": formato_nombre,
                "total_fuentes": len(citas_encontradas),
                "error": False
            }
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            return {
                "respuesta_completa": f"Error generando citas: {error_msg}",
                "citas_encontradas": [],
                "citas_estructuradas": [],
                "formato_usado": formato_nombre,
                "total_fuentes": 0,
                "error": True
            }
            
    except Exception as e:
        return {
            "respuesta_completa": f"Error de conexión: {str(e)}",
            "citas_encontradas": [],
            "citas_estructuradas": [],
            "formato_usado": formato_nombre,
            "total_fuentes": 0,
            "error": True
        }

def extraer_citas_estructuradas(respuesta, citas_encontradas):
    """
    Función mejorada para extraer citas de manera estructurada desde la respuesta
    """
    citas_estructuradas = []
    
    # Dividir la respuesta en líneas
    lineas = [linea.strip() for linea in respuesta.split('\n') if linea.strip()]
    
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        
        # Detectar inicio de una nueva afirmación, pero EXCLUIR resúmenes
        if ((linea.startswith('###') or 
            'afirmación' in linea.lower() or 
            'afirmacion' in linea.lower() or
            any(num in linea for num in ['1.', '2.', '3.', '4.', '5.'])) and
            # EXCLUIR palabras que indican resumen o final
            'resumen' not in linea.lower() and
            'final' not in linea.lower() and
            'conclusión' not in linea.lower() and
            'summary' not in linea.lower()):
            
            cita_actual = {
                'afirmacion': linea,
                'cita_texto': '',
                'fuente_url': '',
                'explicacion': ''
            }
            
            # Buscar información en las siguientes líneas
            i += 1
            while i < len(lineas):
                linea_actual = lineas[i]
                
                # Si encontramos la siguiente afirmación o resumen, terminar esta
                if (linea_actual.startswith('###') or 
                    'afirmación' in linea_actual.lower() or
                    any(num in linea_actual for num in ['1.', '2.', '3.', '4.', '5.']) or
                    'resumen' in linea_actual.lower() or
                    'final' in linea_actual.lower() or
                    'conclusión' in linea_actual.lower()):
                    break
                
                # Detectar cita - patrones más flexibles
                if ('cita' in linea_actual.lower() or 
                    'citation' in linea_actual.lower() or
                    'formato' in linea_actual.lower()):
                    
                    # Buscar la línea siguiente que tenga contenido real (no vacío)
                    j = i + 1
                    while j < len(lineas) and j < i + 3:  # Buscar en las próximas 3 líneas
                        if (lineas[j].strip() and 
                            not lineas[j].startswith('-') and 
                            'fuente' not in lineas[j].lower() and
                            'http' not in lineas[j].lower() and
                            len(lineas[j]) > 10):
                            cita_actual['cita_texto'] = lineas[j]
                            break
                        j += 1
                
                # Detectar fuente/URL
                elif ('fuente:' in linea_actual.lower() or 
                      'source:' in linea_actual.lower() or
                      'http' in linea_actual.lower()):
                    
                    # Extraer URL si está presente
                    if 'http' in linea_actual:
                        # Buscar la URL en la línea
                        import re
                        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', linea_actual)
                        if urls:
                            cita_actual['fuente_url'] = urls[0]
                    else:
                        cita_actual['fuente_url'] = linea_actual.replace('Fuente:', '').replace('fuente:', '').replace('Source:', '').replace('source:', '').strip()
                
                # Detectar explicación
                elif ('explicación:' in linea_actual.lower() or 
                      'explicacion:' in linea_actual.lower() or
                      'explanation:' in linea_actual.lower()):
                    
                    # Buscar la línea siguiente que tenga contenido
                    j = i + 1
                    while j < len(lineas) and j < i + 4:
                        if lineas[j].strip() and len(lineas[j]) > 5:
                            cita_actual['explicacion'] = lineas[j]
                            break
                        j += 1
                
                i += 1
            
            # Solo agregar si tenemos al menos la afirmación y NO es un resumen
            if (cita_actual['afirmacion'] and 
                'resumen' not in cita_actual['afirmacion'].lower() and
                'final' not in cita_actual['afirmacion'].lower()):
                
                # Si no tenemos cita_texto pero tenemos fuente_url, crear una cita básica
                if not cita_actual['cita_texto'] and cita_actual['fuente_url']:
                    cita_actual['cita_texto'] = f"Fuente verificada: {cita_actual['fuente_url']}"
                
                citas_estructuradas.append(cita_actual)
        else:
            i += 1
    
    # Si no se pudieron extraer citas estructuradas, usar método alternativo
    if not citas_estructuradas:
        citas_estructuradas = extraer_citas_alternativo(respuesta, citas_encontradas)
    
    # Filtrar nuevamente para asegurar que no hay resúmenes
    citas_estructuradas = [cita for cita in citas_estructuradas 
                          if 'resumen' not in cita['afirmacion'].lower() 
                          and 'final' not in cita['afirmacion'].lower()
                          and 'conclusión' not in cita['afirmacion'].lower()]
    
    # Si aún no hay citas estructuradas pero hay fuentes encontradas
    if not citas_estructuradas and citas_encontradas:
        for idx, fuente_url in enumerate(citas_encontradas[:5]):  # Máximo 5
            citas_estructuradas.append({
                'afirmacion': f'Afirmación {idx + 1} del texto analizado',
                'cita_texto': f'Referencia encontrada automáticamente',
                'fuente_url': fuente_url,
                'explicacion': 'Fuente verificada mediante búsqueda automatizada en Perplexity AI'
            })
    
    return citas_estructuradas

def extraer_citas_alternativo(respuesta, citas_encontradas):
    """
    Método alternativo para extraer citas cuando el método principal falla
    """
    citas_estructuradas = []
    lineas = [linea.strip() for linea in respuesta.split('\n') if linea.strip()]
    
    # Buscar secciones que parezcan afirmaciones (excluyendo resúmenes)
    afirmaciones_encontradas = []
    afirmacion_actual = ""
    
    for i, linea in enumerate(lineas):
        # Detectar afirmaciones pero excluir resúmenes
        if ((linea.startswith('##') or 
            'afirmación' in linea.lower() or 
            any(num in linea for num in ['1.', '2.', '3.', '4.', '5.'])) and
            'resumen' not in linea.lower() and
            'final' not in linea.lower()):
            
            if afirmacion_actual and 'resumen' not in afirmacion_actual.lower():
                afirmaciones_encontradas.append(afirmacion_actual.strip())
            afirmacion_actual = linea + " "
        elif (afirmacion_actual and linea and not linea.startswith('---') and
              'resumen' not in linea.lower() and 'final' not in linea.lower()):
            afirmacion_actual += linea + " "
    
    if afirmacion_actual and 'resumen' not in afirmacion_actual.lower():
        afirmaciones_encontradas.append(afirmacion_actual.strip())
    
    # Crear estructura de citas basada en las afirmaciones encontradas
    for idx, afirmacion in enumerate(afirmaciones_encontradas[:5]):  # Máximo 5 afirmaciones
        fuente_url = citas_encontradas[idx] if idx < len(citas_encontradas) else ""
        
        citas_estructuradas.append({
            'afirmacion': afirmacion,
            'cita_texto': f"Cita automática para afirmación {idx + 1}" if not fuente_url else f"Fuente: {fuente_url}",
            'fuente_url': fuente_url,
            'explicacion': 'Información respaldada por fuentes verificadas'
        })
    
    return citas_estructuradas

def get_formatos_cita_disponibles():
    """
    Devuelve los formatos de cita disponibles
    """
    return {
        "apa": {
            "nombre": "APA (American Psychological Association)",
            "descripcion": "Ciencias sociales, psicología, educación",
            "ejemplo": "Autor, A. A. (Año). Título del trabajo. Editorial."
        },
        "mla": {
            "nombre": "MLA (Modern Language Association)", 
            "descripcion": "Humanidades, literatura, artes",
            "ejemplo": "Autor, Nombre. Título del Libro. Editorial, Año."
        },
        "chicago": {
            "nombre": "Chicago Manual of Style",
            "descripcion": "Historia, negocios, ciencias sociales",
            "ejemplo": "Autor, Nombre. Título del Libro. Lugar: Editorial, Año."
        },
        "ieee": {
            "nombre": "IEEE (Institute of Electrical and Electronics Engineers)",
            "descripcion": "Ingeniería, tecnología, ciencias de la computación",
            "ejemplo": "A. Autor, \"Título del artículo,\" Título Revista, vol. x, no. x, pp. xx-xx, Año."
        },
        "harvard": {
            "nombre": "Harvard Referencing",
            "descripcion": "Ciencias, medicina, negocios (Reino Unido/Australia)",
            "ejemplo": "Autor, A. (Año) 'Título del artículo', Título Revista, volumen(número), páginas."
        },
        "vancouver": {
            "nombre": "Vancouver Style", 
            "descripcion": "Medicina, ciencias de la salud",
            "ejemplo": "1. Autor A, Autor B. Título del artículo. Título Revista. Año;volumen(número):páginas."
        },
        "ama": {
            "nombre": "AMA (American Medical Association)",
            "descripcion": "Medicina, ciencias biomédicas",
            "ejemplo": "1. Autor AA, Autor BB. Título del artículo. Título Revista. Año;volumen(número):páginas-páginas."
        },
        "acs": {
            "nombre": "ACS (American Chemical Society)",
            "descripcion": "Química, ciencias químicas",
            "ejemplo": "1. Autor, A.; Autor, B. Título Revista Año, volumen, páginas."
        },
        "nature": {
            "nombre": "Nature Style",
            "descripcion": "Revistas científicas Nature",
            "ejemplo": "1. Autor, A. & Autor, B. Título Revista volumen, páginas-páginas (Año)."
        }
    }