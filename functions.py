import requests
import json
import pandas as pd
from datetime import datetime
import calendar
from dotenv import load_dotenv
from base_loger import WriteLogger
import os


# Fucnion que crea paths relativos a la ruta del archivo de ejecucion 
def create_path(path):
    '''
    Crea una ruta relativa a la ubicacion del archivo que se esta ejecutando
    Ejemplo: 
    - ./main.py 
    Nueva ruta
    - ./main.py
    - ./nueva/ruta/creada
    '''
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base,path)
        os.makedirs(path,exist_ok=True)
        return path
    except Exception as exc:
        logger(exc)

# Funcion que obtiene la ip publica del equipo
def obtener_ip_publica():
    servicios = [
        'https://api.ipify.org',
        'https://icanhazip.com',
        'https://ident.me',
        'https://checkip.amazonaws.com'
    ]
    for servicio in servicios:
        try:
            respuesta = requests.get(servicio, timeout=5)
            if respuesta.status_code == 200:
                ip = respuesta.text.strip()
                return ip
        except:
            continue
    return None

#Variables wolkvox
load_dotenv()
wolkvox_token = os.getenv("TOKEN")
wolkvox_server = os.getenv("SERVER")
campaign_id = os.getenv("ID_CAMPAIGN")
headers = {
            'wolkvox-token': f'{wolkvox_token}'
        }

#logger
path_logs = create_path(datetime.now().strftime("logs/%Y%m"))
logger = WriteLogger("Liverpool", filename_preffix="Liverpool")

#Control de fechas
def control_fechas(mes):
    mes = int(mes)
    _,end = calendar.monthrange(datetime.now().year,mes)
    if mes>=10:
        date_end = datetime.now().strftime(f"%Y{mes}{end}235900")
        date_ini = datetime.now().strftime(f"%Y{mes}01000000")
    else:
        date_end = datetime.now().strftime(f"%Y0{mes}{end}235900")
        date_ini = datetime.now().strftime(f"%Y0{mes}01000000")
    logger(date_ini,level='debug')
    logger(date_end,level='debug')
    return date_ini, date_end

# Descarga el reporte 3 de la seccion campañas para extraer todos los registros de llamada
def campaign_3(mes, file=False):
    '''
    Funcion encargada de descargar el reporte 3 de campañas
    esta funcion recibe un int que hace referencia al mes a descargar
    y un True o False que define si genera o no un archivo de salida
    el archivo se guarda en una subcarpeta de donde se ejecuta el script principal
    
    Regresa un DataFrame con la data encontrada
    '''
    logger("Ejecución reporte campaña - 3. 'Campaña resultado telefono a telefono'")
    date_ini, date_end = control_fechas(mes)

    try:
        logger("Extrayendo data...")
        url = f"https://wv{wolkvox_server}.wolkvox.com/api/v2/reports_manager.php?api=campaign_3&campaign_id={campaign_id}&date_ini={date_ini}&date_end={date_end}"
        response = requests.request("GET", url, headers=headers, data={})
        if response.status_code == 200:
            data = pd.DataFrame(data=response.json()["data"])
        else:
            logger(response.text)
    except Exception as exc:
        data = pd.DataFrame()
        logger.exception(exc)
        logger(f"Validar que la IP: '{obtener_ip_publica()}' este dada de alta")

    # Validando data y generando file (Si se activa)
    if not data.empty:
        logger(f"Data obtenida {len(data)} registros")
        logger(data.head())
        if file:
            path = create_path(datetime.now().strftime("data/%Y%m"))
            logger("Creando archivo de salida:",os.path.join(path,datetime.now().strftime("Llamadas_%Y%m%d.xlsx")))
            data.to_excel(os.path.join(path,datetime.now().strftime("Llamadas_%Y%m%d.xlsx")))
    else:
        logger(f"No se encontraron registros para {date_ini} - {date_end}")
        data = 0
    logger("Extraccion finalizada")
    return data
        
# Funcion que descarga el reporte 1. Detalle de llamadas IVR, de Diagram Reports        
def diagram_reports_1(mes, file=False):
    '''
    Funcion encargada de descargar el reporte 1 de diagram reports
    esta funcion recibe un int que hace referencia al mes a descargar
    y un True o False que define si genera o no un archivo de salida
    el archivo se guarda en una subcarpeta de donde se ejecuta el script principal
    
    Regresa un DataFrame con la data encontrada
    '''
    logger("Ejecución reporte Diagram Reports - '1. Detalle de llamadas IVR'")
    date_ini, date_end = control_fechas(mes)
  
    try:
        logger("Extrayendo data...")
        url = f"https://wv{wolkvox_server}.wolkvox.com/api/v2/reports_manager.php?api=diagram_1&date_ini={date_ini}&date_end={date_end}"
        response = requests.request("GET", url, headers=headers, data={})
        if response.status_code == 200:
            data = pd.DataFrame(data=response.json()["data"])
        else:
            logger(response.text)
    except Exception as exc:
        data = pd.DataFrame()
        logger.exception(exc)
        logger(f"Validar que la IP: '{obtener_ip_publica()}' este dada de alta")

    # Validando data y generando file (Si se activa)    
    if not data.empty:
        logger(f"Data obtenida {len(data)} registros")
        logger(data.head())
        if file:
            path = create_path(datetime.now().strftime("data/%Y%m"))
            logger("Creando archivo de salida:",os.path.join(path,datetime.now().strftime("Llamadas_%Y%m%d.xlsx")))
            data.to_excel(os.path.join(path,datetime.now().strftime("Llamadas_%Y%m%d.xlsx")))
    else:
        logger(f"No se encontraron registros para {date_ini} - {date_end}")
        data = 0
    
    logger("Extraccion finalizada")
    return data
    

def panel_principal(llamadas:pd.DataFrame, tipificaciones: pd.DataFrame, file = False):
    logger("Filtrando reporte '1. Detalle de llamadas IVR' por 'IVR CONVERSACIONAL LIVERPOOL..'")
    tipificaciones = tipificaciones[tipificaciones["rp_name"] == "IVR Conversacional LIVERPOOL"]
    logger(f"Nueva longitud de {len(tipificaciones)}")
    logger("Filtro terminado")

    logger("Creando panel principal")
    df = llamadas.merge(tipificaciones,left_on='conn_id', right_on='conn_id',how='left')

    if file:
        logger("Creando archivo de salida:",os.path.join(path,datetime.now().strftime("Llamadas_%Y%m%d.xlsx")))
        path = create_path(datetime.now().strftime("data/%Y%m"))
        df.to_excel(os.path.join(path,datetime.now().strftime("Llamadas_%Y%m%d.xlsx")))
        logger("Archivo creado")

    # Obteniendo el estatus de llamada (ANSWER, ANSWER-MACHINE, BUSY, NO-ANSWER, CONGESTION, FAILED)
    conteo_estatus_llamada = df.value_counts("result_x")
    logger("Total estatus llamada",conteo_estatus_llamada)

    # Obteniendo la tipificacion del IVR (AGENTE, NO_PASA_AGENTE, CUELGA_LLAMADA, BUZON, PULSE)
    conteo_tipificacion = df.value_counts("cod_opc_menu")
    logger("Total estatus tipificacion",conteo_tipificacion)
    
    # Obteniendo el total de registros unicos
    total_registros = df["telephone"].nunique()
    logger(f"Total registros unicos {total_registros}")

llamadas = campaign_3("5")
tipificaciones = diagram_reports_1("5")

panel_principal(llamadas,tipificaciones, True)
