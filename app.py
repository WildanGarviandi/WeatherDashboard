import os
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
DEFAULT_CITY = os.getenv("CITY", "London")
UNITS = os.getenv("UNITS", "metric")

@app.context_processor
def inject_translation():
    return dict(_=_)

# Simple Translation Dictionary
TRANSLATIONS = {
    'en': {
        "Weather Dashboard": "Weather Dashboard",
        "Update: Just Now": "Update: Just Now",
        "Current Weather": "Current Weather",
        "Humidity": "Humidity",
        "Wind": "Wind",
        "Feels Like": "Feels Like",
        "Recommendation": "Recommendation",
        "7 Day Forecast": "7 Day Forecast",
        "Powered by OpenWeatherMap & Flask": "Powered by OpenWeatherMap & Flask",
    },
    'pt': {
        "Weather Dashboard": "Painel Meteorológico",
        "Update: Just Now": "Atualização: Agora mesmo",
        "Current Weather": "Clima Atual",
        "Humidity": "Umidade",
        "Wind": "Vento",
        "Feels Like": "Sensação Térmica",
        "Recommendation": "Recomendação",
        "7 Day Forecast": "Previsão para 7 Dias",
        "Powered by OpenWeatherMap & Flask": "Movido por OpenWeatherMap e Flask",
    }
}

def _(key):
    # Get language from query param 'lang', default to 'en'
    lang = request.args.get('lang', 'en')
    if lang not in TRANSLATIONS:
        lang = 'en'
    return TRANSLATIONS[lang].get(key, key)

def get_weather(city):
    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={UNITS}"
    current_resp = requests.get(current_url).json()

    if current_resp.get("cod") != 200:
        return None, f"Error fetching weather: {current_resp.get('message')}"

    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={UNITS}"
    forecast_resp = requests.get(forecast_url).json()

    daily_forecasts = []
    for i, entry in enumerate(forecast_resp.get("list", [])):
        if i % 8 == 0:
            daily_forecasts.append(entry)
        if len(daily_forecasts) >= 7: # Limit to 7 days
            break

    return {
        "current": current_resp,
        "forecast": daily_forecasts
    }, None

def get_recommendation(condition):
    condition = condition.lower()
    if "rain" in condition or "drizzle" in condition:
        return {"title": _("Indoor Cozy Vibes"), "text": _("It's raining! Perfect for reading a book with a hot cup of coffee."), "icon": "☕"}
    elif "snow" in condition:
        return {"title": _("Stay Warm"), "text": _("Snowy weather outside. Stay inside and enjoy some warm soup."), "icon": "🍜"}
    elif "clear" in condition or "sunny" in condition:
        return {"title": _("Outdoor Adventure"), "text": _("The sun is shining! A great day for a hike or a picnic."), "icon": "☀️"}
    elif "cloud" in condition:
        return {"title": _("Chill Walk"), "text": _("Overcast but nice. Great time for a light stroll or photography."), "icon": "📸"}
    else:
        return {"title": _("Daily Activity"), "text": _("Enjoy your day regardless of the weather!"), "icon": "🌟"}

@app.route('/')
def index():
    city = request.args.get('q', DEFAULT_CITY)
    data, error = get_weather(city)
    if error:
        return f"<h1>Error</h1><p>{error}</p>", 500

    recommendation = get_recommendation(data['current']['weather'][0]['description'])

    return render_template('index.html',
                           current=data['current'],
                           forecast=data['forecast'],
                           rec=recommendation,
                           city=city)

if __name__ == '__main__':
    app.run(debug=True)
