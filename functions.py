import requests
import json
import pandas as pd
from datetime import datetime
import calendar


path_config = r"DashboardsWolkvox/config/config.json"
config = json.loads(open(path_config).read())

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

def get_calls(config, operacion, campaign_id, mes):
    print("Ejecución reporte Llamadas")
    token = config[operacion]["token"]
    server = config[operacion]["server"]
    mes = int(mes)
    _,end = calendar.monthrange(datetime.now().year,mes)
    if mes>=10:
        date_end = datetime.now().strftime(f"%Y{mes}{end}235900")
        date_ini = datetime.now().strftime(f"%Y{mes}01000000")
    else:
        date_end = datetime.now().strftime(f"%Y0{mes}{end}235900")
        date_ini = datetime.now().strftime(f"%Y0{mes}01000000")
    print(date_ini)
    print(date_end)
    try:
        headers = {
            'wolkvox-token': f'{token}'
        }
        url = f"https://wv{server}.wolkvox.com/api/v2/reports_manager.php?api=campaign_3&campaign_id={campaign_id}&date_ini={date_ini}&date_end={date_end}"
        response = requests.request("GET", url, headers=headers, data={})
        data = pd.DataFrame(data=response.json()["data"])
        print(data["customer_id"].head())
    except requests.exceptions.ConnectionError:
        print(f"Validar que la IP: '{obtener_ip_publica()}' este dada de alta")
        return {
            "status" : 404,
            "mensaje" : f"Validar que la IP: '{obtener_ip_publica()}' este dada de alta",
            "data" : f"Validar que la IP: '{obtener_ip_publica()}' este dada de alta"
        }

# def reporte_llamadas():
#   print("Ejecución reporte Llamadas")
#   campaign_id = config["campaign_id"]
#   url_llamadas = f"https://wv{wolkvox_server}.wolkvox.com/api/v2/reports_manager.php?api=campaign_3&campaign_id={campaign_id}&date_ini={date_ini}&date_end={date_end}"
#   response = requests.request("GET", url_llamadas, headers=headers, data=payload)
#   if response.status_code == 200:
#     #Transformando la respuesta a json
#     result = response.text
#     result = json.loads(result)

#     #Genrando archivo de salida txt separado por comas
#     df = pd.DataFrame(data=result["data"])
#     print(df.head(5))
#     # df.to_csv(os.path.join(config["path_data"],f"Llamadas_{date_ini[:8]}.txt"),sep=separador, index=False)
#     print("Reporte llamadas finalizado correctamente")
#   else:
#     print("Reporte llamadas con error")
#     #Generando archivo con respuesta de error
#     with open(os.path.join(config["path_data"],f"Llamadas_{date_ini[:6]}.txt"), 'w') as file:
#         file.write(response.text)

get_calls(config, "promass","25574","5")