import base64
import math

import requests


def get_cords(geocode):
    server_address = 'http://geocode-maps.yandex.ru/1.x/?'
    api_key_1 = '8013b162-6b42-4997-9691-77b7074026e0'
    geocoder_request = f'{server_address}apikey={api_key_1}&geocode={geocode}&format=json'
    response = requests.get(geocoder_request)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    return toponym["Point"]["pos"].split()


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = map(float, a)
    b_lon, b_lat = map(float, b)
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)

    return int(distance)


def get_response_as_base64(point, zoom):
    map_params = {
        "ll": ','.join(map(str, point)),
        "z": zoom,
        "size": "600,400",
        'l': 'sat',
    }
    map_api_server = "https://static-maps.yandex.ru/1.x"

    try:
        response = requests.get(map_api_server, params=map_params)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе карты: {e}")
        return None
