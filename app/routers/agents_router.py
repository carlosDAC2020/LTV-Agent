from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Any 

# servicio de agentes
from app.services.agents.agent import LTV_agent
from app.services.utils.utils import json_extraction

import asyncio
import time

router = APIRouter(
    prefix="/agent",
    tags=["agent"]  # Etiqueta para la documentación de Swagger
)

@router.post("/ltv/http", response_model=Any)
async def analyze(data: dict):
    prompt_input = data["text"]
    print("iniciamos el agente")
    time_start = time.time()
    async with LTV_agent.run() as agent:
        # Llama al agente en cadena
        print("enviamos el propmt")
        result = await agent.ltv_full_process.send(prompt_input)

    # obtehnemos contexto 
    context_propmt = f"""
        initial news : {prompt_input}
        information items : {result}
    """
    result = await agent.context_items.send(context_propmt)

    # obtenemos el puntaje de veracidad
    result = await agent.veracity_score.send(result)
    
    data = json_extraction(result)

    time_end = time.time()
    print(f" tiempo de ejcucion del agente: {time_end - time_start} segundos")
    print("agente finalizado")
    return data

@router.websocket("/ltv/ws")
async def analyze_websocket_step_by_step(websocket: WebSocket):
    await websocket.accept()
    print("Cliente conectado al WebSocket para análisis paso a paso.")
    
    try:
        initial_data = await websocket.receive_json()
        prompt_input = initial_data.get("text")
        if not prompt_input:
            await websocket.send_json({"status": "error", "step_name": "initialization", "message": "No se recibió el texto a analizar."})
            return

        time_start = time.time()
        
        async with LTV_agent.run() as agent:
            # --- PASO 1: keywords_extraction ---
            await websocket.send_json({"status": "processing", "step": 1, "step_name": "keywords_extraction", "message": "Extrayendo palabras clave..."})
            result_step1 = await agent.keywords_extraction.send(prompt_input)
            data_step1 = json_extraction(result_step1)
            await websocket.send_json({"status": "completed", "step": 1, "step_name": "keywords_extraction_completed", "data": data_step1})

            # --- PASO 2: brave_search ---
            await websocket.send_json({"status": "processing", "step": 2, "step_name": "brave_search", "message": "Buscando en Brave..."})
            # El input para la búsqueda es el resultado del paso anterior
            result_step2 = await agent.brave_search.send(result_step1)
            data_step2 = json_extraction(result_step2)
            await websocket.send_json({"status": "completed", "step": 2, "step_name": "brave_search_completed", "data": data_step2})
            
            # --- PASO 3: normalize_results ---
            await websocket.send_json({"status": "processing", "step": 3, "step_name": "normalize_results", "message": "Normalizando resultados de búsqueda..."})
            result_step3 = await agent.normalize_results.send(result_step2)
            data_step3 = json_extraction(result_step3)
            await websocket.send_json({"status": "completed", "step": 3, "step_name": "normalize_results_completed", "data": data_step3})

            # --- PASO 4: inference_items ---
            await websocket.send_json({"status": "processing", "step": 4, "step_name": "inference_items", "message": "Realizando inferencias sobre los items..."})
            result_step4 = await agent.inference_items.send(result_step3)
            data_step4 = json_extraction(result_step4)
            await websocket.send_json({"status": "completed", "step": 4, "step_name": "inference_items_completed", "data": data_step4})

            # --- PASO 5: confidence_items ---
            await websocket.send_json({"status": "processing", "step": 5, "step_name": "confidence_items", "message": "Calculando confianza de los items..."})
            result_step5 = await agent.confidence_items.send(result_step4)
            data_step5 = json_extraction(result_step5)
            await websocket.send_json({"status": "completed", "step": 5, "step_name": "confidence_items_completed", "data": data_step5})

            # --- PASO 6: context_items (Usa una herramienta MCP) ---
            await websocket.send_json({"status": "processing", "step": 6, "step_name": "context_items", "message": "Calculando contexto semántico..."})
            context_propmt = f"""
                initial news : {prompt_input}
                information items : {data_step5}
            """
            result_step6 = await agent.context_items.send(context_propmt)
            data_step6 = json_extraction(result_step6)
            await websocket.send_json({"status": "completed", "step": 6, "step_name": "context_items_completed", "data": data_step6})

            # --- PASO 7: veracity_score (Usa una herramienta MCP) ---
            await websocket.send_json({"status": "processing", "step": 7, "step_name": "veracity_score", "message": "Calculando puntaje final de veracidad..."})
            result_step7 = await agent.veracity_score.send(data_step6)
            data_step7 = json_extraction(result_step7)
            
            # --- Enviar resultado final ---
            time_end = time.time()
            total_time = time_end - time_start
            
            await websocket.send_json({
                "status": "final_result",
                "message": "Proceso finalizado.",
                "execution_time": total_time,
                "data": data_step7
            })
            
            print(f"Tiempo total de ejecución del agente: {total_time:.2f} segundos")

    except WebSocketDisconnect:
        print("Cliente desconectado.")
    except Exception as e:
        print(f"Error inesperado en el WebSocket: {e}")
        await websocket.send_json({"status": "error", "message": f"Ha ocurrido un error inesperado: {str(e)}"})
    finally:
        await websocket.close()
        print("Conexión WebSocket cerrada.")