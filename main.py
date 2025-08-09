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


city_cords = {"Tampa": (28.0, -82.5),
              "New York": (40.7, -74.0),
              "Los Angeles": (34.05, -118.25)}

city_names = list(city_cords.keys())
formatted_latitudes = ",".join([str(value[0]) for value in list(city_cords.values())])
formatted_longitudes = ",".join([str(value[1]) for value in list(city_cords.values())])

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
    

def fetchForecasts(city_cords: dict):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": formatted_latitudes,
        "longitude": formatted_longitudes,
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit",
        "forecast_days": 3,
        "past_days": 3
    }
    
    responses = openmeteo.weather_api(url, params=params)
    return responses
    
def displayData(name, response):
    city = response[0]
    
    #Location Info
    print(f"\nCity: {name}")
    print(f"Coordinates: {city.Latitude()}°N {city.Longitude()}°E")
    print(f"Elevation: {city.Elevation()} m asl")

    #Hourly Data
    hourly = city.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    max_temp = max(hourly_temperature_2m)
    average_temp = sum(hourly_temperature_2m) / len(hourly_temperature_2m)
    
    print(f"Average Temperature (6 day): {average_temp:.2f} °F")
    print(f"Maximum Temperature (6 day): {max_temp:.2f} °F")
    
def main():
    query = input("Search: ")
    name, coordinates = fetchCoordinates(query)
    response = fetchForecasts(coordinates)
    displayData(name, response)
   
if __name__ == "__main__":
    main()