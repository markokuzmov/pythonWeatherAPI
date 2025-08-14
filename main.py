from flask import Flask, request, jsonify, redirect, url_for, render_template

import openmeteo_requests

import requests_cache
import requests
from retry_requests import retry

from dotenv import load_dotenv
import os

import urllib.parse

load_dotenv()
geocoding_api_key = os.getenv("GEOCODING_API_KEY")

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

app = Flask(__name__)

def fetchCoordinates(city: str):
    url = f"https://geocode.maps.co/search"
    params = {
        "q": urllib.parse.quote_plus(city),
        "api_key": geocoding_api_key
    }
    
    responses = requests.get(url=url, params=params)
    response = responses.json()[0]
    name = response['display_name']
    coordinates = (response['lat'], response['lon'])
    
    return name, coordinates
    

def fetchForecasts(coordinates):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coordinates[0],
        "longitude": coordinates[1],
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit",
        "forecast_days": 3,
        "past_days": 3
    }
    
    responses = openmeteo.weather_api(url, params=params)
    return responses

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/forecast", methods=["GET"])
def forecast():
    location = request.args.get("location")
    if not location:
        return jsonify({"error": "No location parameter"}), 400
    
    name, coordinates = fetchCoordinates(location)
    forecast = fetchForecasts(coordinates)
    location_data = forecast[0]
    hourly = location_data.Hourly().Variables(0).ValuesAsNumpy()
    data = {
        "location": name,
        "coordinates": {
            "lat": location_data.Latitude(),
            "lon": location_data.Longitude()
        },
        "elevation": location_data.Elevation(),
        "average_temp": float(sum(hourly) / len(hourly)),
        "max_temp": float(max(hourly))
    }
    
    return render_template("weather.html", weather=data)

if __name__ == "__main__":
    app.run(debug=True)