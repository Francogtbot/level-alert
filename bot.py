import os
import requests
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
UMBRAL_USD = 250
ORIGEN = 'SCL'
DESTINO = 'BCN'
CABINA = 'economy'

def obtener_precio():
    today = datetime.today().strftime('%Y%m%d')
    url = 'https://www.flylevel.com/en/ndc/flightcalendar/FlightCalendarPricesLevel'
    params = {'origin':ORIGEN,'destination':DESTINO,
              'startDate':today,'lengthOfStay':7,
              'cabinClass':CABINA,'currency':'USD'}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print(f"Error en la petición: {resp.status_code}")
        print(resp.text)
        return []
    try:
        data = resp.json()
    except ValueError as e:
        print("Error al decodificar JSON:", e)
        print(resp.text)
        return []
    precios=[]
    for item in data.get('Result',[]):
        trip_price=float(item.get('Items',[''])[0].split(';')[2])
        precios.append((item.get('FlightDate'),trip_price))
    return precios

def enviar_telegram(texto):
    url=f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID,'text':texto})

def tarea():
    precios=obtener_precio()
    bajos=[(d,p) for d,p in precios if p<=UMBRAL_USD]
    if bajos:
        msg=f"Precios bajo USD {UMBRAL_USD}:\n"
        for d,p in bajos:
            msg+=f"- {d}: USD {p:.2f}\n"
        enviar_telegram(msg)

if __name__=='__main__':
    tarea()
