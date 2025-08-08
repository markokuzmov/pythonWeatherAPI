import openmeteo_requests

import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)


city_cords = {"Tampa": (28.0, -82.5),
              "New York": (40.7, -74.0),
              "Los Angeles": (34.05, -118.25)}

city_names = list(city_cords.keys())
formatted_latitudes = ",".join([str(value[0]) for value in list(city_cords.values())])
formatted_longitudes = ",".join([str(value[1]) for value in list(city_cords.values())])

url = "https://api.open-meteo.com/v1/forecast"

def fetchForecasts(city_cords):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": formatted_latitudes,
        "longitude": formatted_longitudes,
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit"
    }
    
    responses = openmeteo.weather_api(url, params=params)
    return responses
    
def displayData(responses):
    for i in range(len(responses)):
        city = responses[i]
        
        #Location Info
        print(f"\nCity: {city_names[i]}")
        print(f"Coordinates: {city.Latitude()}°N {city.Longitude()}°E")
        print(f"Elevation: {city.Elevation()} m asl")
    
        #Hourly Data
        hourly = city.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        max_temp = max(hourly_temperature_2m)
        average_temp = sum(hourly_temperature_2m) / len(hourly_temperature_2m)
        # Daily averag
        # for day in hourly_temperature_2m:
        #     average_temp = sum(day.temps) / len(day.temps)
        #     print(f"Average Temperature for {day}: {average_temp:.2f} °F")
        print(f"Average Temperature: {average_temp:.2f} °F")
        print(f"Maximum Temperature: {max_temp:.2f} °F")
    
def main():
    responses = fetchForecasts(city_cords)
    displayData(responses)
   
if __name__ == "__main__":
    main()