import json
import io
import pandas as pd
from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse

from app.services.functions import panel_principal, get_details_tipificacion, get_details_numero
from app.services.wolkvox_api import ejecutar_accion

router = APIRouter()

@router.get("/ivr-status/{estatus}")
async def detalle_estatus(estatus: str):
    df = get_details_tipificacion(5,estatus)    
    return df.to_dict(orient="records")

@router.get("/bot-status/{estatus}")
async def detalle_estatus(estatus: str):
    df = get_details_numero(5,estatus)    
    return df.to_dict(orient="records")

@router.get("/panel-principal")
async def obtener_grafica_estatus():
    # ... Aquí ejecutas tu código de Pandas ...
    total_registros, conteo_estatus_llamada, conteo_tipificacion, conteo_remarcaciones = panel_principal(5)
    
    # Convertimos los datos de Pandas a listas nativas de Python
    bot_etiquetas = conteo_tipificacion.index.tolist()       # ['CV_AGENTE','CV_CUELGA_LLAMADA']
    bot_porcentajes = conteo_tipificacion["porcentaje"].tolist() # [71.4, 28.6]
    
    return {
        "status": "success",
        "data": {
            "bot_etiquetas" : bot_etiquetas,
            "bot_porcentajes" : bot_porcentajes
        }
    }


# Estas son variables que vienen del form
# Todos los elementos deben existir dentro del mismo
# los nombre de la izquierda hacen referencia a "name" del elemento para poderlo referenciar
@router.post("/ejecutar")
async def ejecutar(
    config: str = Form(...),
    accion: str = Form(...),
    archivo: UploadFile = File(None)):


    # Mandamos llamar a la funcion que es quien controla todo el backend
    resultado = await ejecutar_accion(accion)

    return JSONResponse(
        status_code=resultado["status"],
        content={
            "mensaje": "",
            "data" : "mensaje de prueba"
        }
    )