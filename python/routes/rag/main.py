from flask import Blueprint, render_template, request, flash, jsonify
from integraciones.ejercicio_1 import retornarContecto, get_consulta_rag_mistral, get_consulta_rag_ollama, get_consulta_rag_gemini, get_consulta_rag_claude, get_consulta_rag_deepseek, get_consulta_rag_openai

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