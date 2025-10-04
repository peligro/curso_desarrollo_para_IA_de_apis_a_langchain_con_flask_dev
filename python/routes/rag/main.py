from flask import Blueprint, render_template, request, flash, redirect, url_for
from integraciones.ejercicio_1 import retornarContecto, get_consulta_rag_mistral, get_consulta_rag_ollama, get_consulta_rag_gemini, get_consulta_rag_claude, get_consulta_rag_deepseek, get_consulta_rag_openai
from integraciones.ejercicio_2 import RecetasRAG, get_recetas_rag
import os
import time

rag_bp = Blueprint('rag', __name__)



@rag_bp.route('/rag')
def rag_index():
    return render_template('rag/index.html')

@rag_bp.route('/rag/atencion-al-cliente', methods=['GET', 'POST'])
def rag_chatbot_atencion_cliente():
    respuesta = None
    tiempo_transcurrido = None
    ia = None
    
    if request.method == 'POST':
        ia = request.form.get('ia', '').strip()
        pregunta = request.form.get('prompt', '').strip()
        if not pregunta or not ia:
            flash('Por favor ingresa una pregunta', 'warning')
        else:
            try:
                inicio = time.time()
                
                contexto_pdf=retornarContecto()
                
                if not contexto_pdf:
                    respuesta = "Error: No se pudo leer el PDF del manual"
                else:
                    if ia=="Ollama":
                        respuesta = get_consulta_rag_ollama(pregunta, contexto_pdf)
                    if ia=="Mistral":
                        respuesta = get_consulta_rag_mistral(pregunta, contexto_pdf)
                    if ia=="Gemini":
                        respuesta = get_consulta_rag_gemini(pregunta, contexto_pdf)
                    if ia=="Claude":
                        respuesta = get_consulta_rag_claude(pregunta, contexto_pdf)
                    if ia=="Deepseek":
                        respuesta = get_consulta_rag_deepseek(pregunta, contexto_pdf)
                    if ia=="OpenAI":
                        respuesta = get_consulta_rag_openai(pregunta, contexto_pdf)

                fin = time.time()
                tiempo_transcurrido = round(fin - inicio, 2)
                
            except Exception as e:
                respuesta = f"Error procesando la consulta: {str(e)}"
                tiempo_transcurrido = 0
    
    return render_template('rag/atencion_cliente.html', 
                         respuesta=respuesta, 
                         tiempo_transcurrido=tiempo_transcurrido,
                         ia=ia)



# routes/rag_recetas.py

@rag_bp.route('/rag/buscador-recetas', methods=['GET', 'POST'])
def rag_buscador_recetas():
    respuesta = None
    tiempo_transcurrido = None
    ia = None
    recetas_encontradas = []
    
    if request.method == 'POST':
        ia = request.form.get('ia', '').strip()
        consulta = request.form.get('consulta', '').strip()
        
        if not consulta or not ia:
            flash('Por favor ingresa una consulta y selecciona una IA', 'warning')
        else:
            try:
                inicio = time.time()
                
                # Inicializar y cargar datos si es la primera vez
                rag_recetas = RecetasRAG()
                
                # Verificar si el índice está vacío y cargar datos de ejemplo
                stats = rag_recetas.index.describe_index_stats()
                if stats.total_vector_count == 0:
                    rag_recetas.cargar_recetas_ejemplo()
                    flash('Se cargaron recetas de ejemplo en la base de datos', 'info')
                
                # Buscar recetas
                recetas_encontradas = rag_recetas.buscar_recetas_similares(consulta)
                respuesta = get_recetas_rag(ia, consulta)
                
                fin = time.time()
                tiempo_transcurrido = round(fin - inicio, 2)
                
            except Exception as e:
                respuesta = f"Error procesando la consulta: {str(e)}"
                tiempo_transcurrido = 0
    
    return render_template('rag/buscador_recetas.html', 
                         respuesta=respuesta,
                         recetas_encontradas=recetas_encontradas,
                         tiempo_transcurrido=tiempo_transcurrido,
                         ia=ia)


@rag_bp.route('/rag/actualizar-base-datos', methods=['POST'])
def actualizar_base_datos():
    """Ruta específica para actualizar la base de datos"""
    try:
        rag_recetas = RecetasRAG()
        resultado = rag_recetas.limpiar_y_cargar_desde_json()
        flash(f'✅ {resultado}', 'success')
    except Exception as e:
        flash(f'❌ Error actualizando base de datos: {str(e)}', 'error')
    
    return redirect(url_for('rag.rag_buscador_recetas'))