import json
import io
import pandas as pd
from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse

from app.services.functions import panel_principal
from app.services.wolkvox_api import ejecutar_accion

router = APIRouter()
@router.get("/panel-principal")
async def obtener_grafica_estatus():
    # ... Aquí ejecutas tu código de Pandas ...
    total_registros, conteo_estatus_llamada, conteo_tipificacion, conteo_remarcaciones = panel_principal(5)
    
    # Convertimos los datos de Pandas a listas nativas de Python
    etiquetas = conteo_tipificacion.index.tolist()       # ['ANSWER', 'NO-ANSWER']
    porcentajes = conteo_tipificacion["porcentaje"].tolist() # [71.4, 28.6]
    
    return {
        "status": "success",
        "labels": etiquetas,
        "data": porcentajes
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