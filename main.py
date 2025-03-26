import random
import requests

map_file = "map.png"


def get_cords(geocode):
    server_address = 'http://geocode-maps.yandex.ru/1.x/?'
    api_key_1 = '8013b162-6b42-4997-9691-77b7074026e0'
    geocoder_request = f'{server_address}apikey={api_key_1}&geocode={geocode}&format=json'
    response = requests.get(geocoder_request)
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    return toponym["Point"]["pos"].split()


def get_response(point, zoom):
    apikey = "b4755c84-fd7e-4198-bb38-654e90e7d54c"
    map_params = {
        "ll": ','.join(point),
        "z": zoom,
        "size": ",".join([str(600), str(400)]),
        'l': 'sat'
    }
    map_api_server = "https://static-maps.yandex.ru/1.x"

    try:
        response = requests.get(map_api_server, params=map_params)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе карты: {e}")
        return None


def change_map(response):
    if response:
        with open(map_file, "wb") as file:
            file.write(response.content)


city = ['Москва', 'Нью-Йорк', 'Токио', 'Париж', 'Сидней', 'Кейптаун']

cords = [
    get_response(get_cords(i), '13') for i in city
]

change_map(cords[random.randint(0, 5)])
