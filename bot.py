import requests
import datetime
import os

# Parámetros del vuelo
origin = "SCL"
destination = "BCN"
currency = "USD"
threshold_usd = 500  # Umbral en dólares
date_from = (datetime.datetime.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
date_to = (datetime.datetime.today() + datetime.timedelta(days=40)).strftime("%Y-%m-%d")

# API URL
url = (
    f"https://www.flylevel.com/en/ndc/flightcalendar/FlightCalendarPricesLevel?"
    f"origin={origin}&destination={destination}&originDepartureDate={date_from}"
    f"&destinationReturnDate={date_to}&tripType=ROUND_TRIP&currencyCode={currency}&adt=1&chd=0&inf=0"
)

# Encabezados para evitar error 403
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        raise Exception("Acceso denegado (403). Verifica User-Agent o si bloquearon bots.")
    response.raise_for_status()
    data = response.json()
    
    # Obtener la fecha y precio más bajo
    lowest_price = float("inf")
    best_date = None

    for date, price_info in data.get("outboundCalendar", {}).items():
        price = price_info.get("lowestFare")
        if price and price < lowest_price:
            lowest_price = price
            best_date = date

    if lowest_price < threshold_usd:
        # Enviar mensaje por Telegram
        message = (
            f"🔔 ¡Precio bajo detectado! Vuelo {origin} → {destination}\n"
            f"📅 Fecha: {best_date}\n"
            f"💸 Precio: ${lowest_price} USD\n"
            f"✈️ Nivel inferior a tu umbral de ${threshold_usd} USD"
        )
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        telegram_response = requests.post(telegram_url, data=payload)
        telegram_response.raise_for_status()
    else:
        print(f"Ningún precio bajo umbral. Mínimo: {lowest_price} USD")

except Exception as e:
    print("Error en la petición:", e)
# test
