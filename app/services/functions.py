import requests
import json
import pandas as pd
from datetime import datetime
import calendar
from dotenv import load_dotenv
import os
import sys
# Obtiene la ruta de la carpeta actual y sube un nivel (al padre)
dir_actual = os.path.dirname(os.path.abspath(__file__))
dir_padre = os.path.dirname(dir_actual)

# Inserta el directorio padre al principio de la lista de rutas de Python
sys.path.insert(0, dir_padre)

# Ahora puedes importar tu archivo y función normalmente
from base_loger import WriteLogger


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
        print(exc)

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
# path_logs = create_path(datetime.now().strftime("logs/%Y%m"))
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
        response = requests.request("GET", url, headers=headers, data={}, timeout=90)
        if response.status_code == 200:
            data = pd.DataFrame(data=response.json()["data"])
        else:
            logger(response.text)
            return pd.DataFrame()
    except Exception as exc:
        logger.exception(exc)
        logger(f"Validar que la IP: '{obtener_ip_publica()}' este dada de alta")
        return pd.DataFrame()

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
        data = pd.DataFrame()
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
        response = requests.request("GET", url, headers=headers, data={}, timeout=90)
        if response.status_code == 200:
            data = pd.DataFrame(data=response.json()["data"])
        else:
            logger(response.text)
            return pd.DataFrame()
    except Exception as exc:
        logger.exception(exc)
        logger(f"Validar que la IP: '{obtener_ip_publica()}' este dada de alta")
        return pd.DataFrame()

    # Validando data y generando file (Si se activa)    
    if not data.empty:
        logger(f"Data obtenida {len(data)} registros")
        logger(data.head())
        if file:
            path = create_path(datetime.now().strftime("data/%Y%m"))
            logger("Creando archivo de salida:",os.path.join(path,datetime.now().strftime("Tipificaciones_%Y%m%d.xlsx")))
            data.to_excel(os.path.join(path,datetime.now().strftime("Tipificaciones_%Y%m%d.xlsx")))
    else:
        logger(f"No se encontraron registros para {date_ini} - {date_end}")
        data = pd.DataFrame()
    
    logger("Extraccion finalizada")
    return data
    
#Generacion de resumen de la informacion
def crear_reportes(mes, file = False):
    #Generando reportes
    llamadas = campaign_3(mes)
    tipificaciones = diagram_reports_1(mes)

    if llamadas.empty:
        logger("No se encontro informacion de Llamadas")
        return pd.DataFrame()
    if tipificaciones.empty:
        logger("No se encontro informacion de Tipificaciones")
        return pd.DataFrame()
    logger("Filtrando reporte '1. Detalle de llamadas IVR' por 'IVR CONVERSACIONAL LIVERPOOL..'", level='debug')
    tipificaciones = tipificaciones[tipificaciones["rp_name"] == "IVR Conversacional LIVERPOOL"]
    logger(f"Nueva longitud de {len(tipificaciones)}", level='debug')
    logger("Filtro terminado", level='debug')

    logger("Creando panel principal")
    # Generando Dataframe unificado con llamadas y tipificaciones
    df = llamadas.merge(tipificaciones,left_on='conn_id', right_on='conn_id',how='left').fillna("N/D").replace("", "N/D")

    if file:
        path = create_path(datetime.now().strftime("data/%Y%m"))
        logger("Creando archivo de salida:",os.path.join(path,datetime.now().strftime("Union_%Y%m%d.xlsx")))
        df.to_excel(os.path.join(path,datetime.now().strftime("Union_%Y%m%d.xlsx")), index=False)
        logger("Archivo creado")
    
    return df

def panel_principal(mes):

    # Buscando archivo base
    path = f"{dir_actual}/{datetime.now().strftime('data/%Y%m/Union_%Y%m%d.xlsx')}"
    logger(f"Buscando archivo {path}")
    if os.path.exists(path):
        df = pd.read_excel(path)
        logger("Archivo encontrado")
    else:
        logger("Archivo no encontrado, creandolo...")
        df = crear_reportes(mes,True)

    if df.empty:
        logger("No se encontro informacion de Llamadas")
        return 0,pd.DataFrame(),pd.DataFrame(),pd.DataFrame()


    # Obteniendo el total de registros unicos
    total_registros = df["telephone"].nunique()
    logger(f"Usuarios recibidos ({total_registros})")

    # Obteniendo el estatus de llamada (ANSWER, ANSWER-MACHINE, BUSY, NO-ANSWER, CONGESTION, FAILED)
    conteo_estatus_llamada = df["result_x"].value_counts().to_frame("cantidad")
    conteo_estatus_llamada["porcentaje"] = (conteo_estatus_llamada["cantidad"]/conteo_estatus_llamada["cantidad"].sum()*100).round(2)
    logger(f"Total estatus llamada ({conteo_estatus_llamada['cantidad'].sum()})",conteo_estatus_llamada)
    # Generando umbrales
    alertas_llamadas = conteo_estatus_llamada[conteo_estatus_llamada["porcentaje"] > 30]
    logger(f"Revisar problema", alertas_llamadas)

    # Obteniendo la tipificacion del IVR (AGENTE, NO_PASA_AGENTE, CUELGA_LLAMADA, BUZON, PULSE)
    conteo_tipificacion = df["cod_opc_menu"].value_counts().to_frame("cantidad").drop("N/D")
    conteo_tipificacion["porcentaje"] = (conteo_tipificacion["cantidad"]/conteo_tipificacion["cantidad"].sum()*100).round(2)
    logger(f"Total estatus bot ({conteo_tipificacion['cantidad'].sum()})",conteo_tipificacion)
    # Generando umbrales
    alertas_tipificacion = conteo_tipificacion[conteo_tipificacion["porcentaje"] > 30]
    logger(f"Revisar problema", alertas_tipificacion)

    # Obteniendo remarcaciones
    conteo_remarcaciones = df["customer_id_x"].value_counts().value_counts().to_frame("cantidad")
    conteo_remarcaciones["porcentaje"] = (conteo_remarcaciones["cantidad"]/conteo_remarcaciones["cantidad"].sum()*100).round(2)
    conteo_remarcaciones.index = conteo_remarcaciones.index.map(lambda x: f"{x} Intento(s)")
    logger(f"Total remarcaciones",conteo_remarcaciones)
    logger("Proceso finalizado")

    return total_registros, conteo_estatus_llamada, conteo_tipificacion, conteo_remarcaciones

# Obtener detalles por tifipifacion de bot
def get_details_tipificacion(mes, tipificacion):
    # Buscando archivo base
    path = f"{dir_actual}/{datetime.now().strftime('data/%Y%m/Union_%Y%m%d.xlsx')}"
    logger(f"Buscando archivo {path}")
    if os.path.exists(path):
        df = pd.read_excel(path)
        logger("Archivo encontrado")
    else:
        logger("Archivo no encontrado, creandolo...")
        df = crear_reportes(mes,True)

    if df.empty:
        logger("No se encontro informacion")
        return pd.DataFrame()
    logger(f"Obteniendo detalles de {tipificacion}")
    df_tipificacion = df[df['cod_opc_menu'] == tipificacion]
    df_tipificacion = df_tipificacion[["customer_id_x","customer_name","telephone","date_x","result_x","cod_opc_menu","opt8","opt12"]]
    logger(df_tipificacion)
    return df_tipificacion

# Obtener detalles por numero de telefono
def get_details_numero(mes, numero):
    # Buscando archivo base
    path = f"{dir_actual}/{datetime.now().strftime('data/%Y%m/Union_%Y%m%d.xlsx')}"
    logger(f"Buscando archivo {path}")
    if os.path.exists(path):
        df = pd.read_excel(path)
        logger("Archivo encontrado")
    else:
        logger("Archivo no encontrado, creandolo...")
        df = crear_reportes(mes,True)

    if df.empty:
        logger("No se encontro informacion")
        return pd.DataFrame()

    logger(f"Obteniendo detalles de {numero}")
    df_llamadas = df[df['telephone'] == int(numero)]
    df_llamadas = df_llamadas[["customer_id_x","customer_name","telephone","date_x","result_x","cod_opc_menu","opt8","opt12"]]
    if df_llamadas.empty:
        logger(f"No se encontraron registros de {numero}")
        return pd.DataFrame()
    else:
        logger(df_llamadas)
        return df_llamadas

# total_registros, conteo_estatus_llamada, conteo_tipificacion, conteo_remarcaciones = panel_principal(5)
# df_tipificacion = get_details_tipificacion(5,"CV_BUZON")
# df_llamadas = get_details_numero(5,"9526671619595")
