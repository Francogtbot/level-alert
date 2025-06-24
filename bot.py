import requests
import os
from datetime import datetime

# ——— CONFIGURACIÓN ———
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
UMBRAL_USD = 500
ORIGEN = 'SCL'
DESTINO = 'BCN'
CURRENCY = 'USD'

# ——— HEADERS ———
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.flylevel.com/",
    "Authorization": "MET eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...TU_TOKEN_AQUI..."  # <— tu token MET
}

def obtener_precios():
    url = "https://www.flylevel.com/en/ndc/flightcalendar/FlightCalendarPricesLevel"
    today = datetime.today().strftime("%Y%m%d")
    params = {
        "origin": ORIGEN,
        "destination": DESTINO,
        "startDate": today,
        "numDays": 60,
        "currencyCode": CURRENCY
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"Error {resp.status_code}")
        print(resp.text)
        return []
    data = resp.json()
    return [(item['FlightDate'], float(item['Items'][0].split(';')[2]))
            for item in data.get('Result', [])]

def enviar_telegram(msj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': msj})

def tarea():
    precios = obtener_precios()
    bajos = [(d, p) for d, p in precios if p <= UMBRAL_USD]
    if bajos:
        msg = f"🎉 Precios bajo USD {UMBRAL_USD}:\n"
        msg += "\n".join(f"- {d}: USD {p:.2f}" for d, p in bajos)
        enviar_telegram(msg)
    else:
        print("Ningún precio bajo.")

if __name__ == "__main__":
    tarea()
