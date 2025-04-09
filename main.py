from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import io
import base64
import random
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app)
n = 13


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


# Функция для генерации случайного изображения (цветной квадрат)
def generate_map_image(zoom):
    city = ['Москва']

    cords = [
        get_response(get_cords(i), str(zoom)) for i in city
    ]
    img_str = base64.b64encode(cords[0].content).decode("utf-8")
    return img_str


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# Обработчик WebSocket-запроса на обновление изображения
@socketio.on('request_plus_image')
def handle_image_request():
    global n
    img_data = generate_map_image(n)
    emit('update_image', {'image_data': img_data})
    n += 1


@socketio.on('request_dif_image')
def handle_image_request():
    global n
    img_data = generate_map_image(n)
    emit('update_image', {'image_data': img_data})
    n -= 1


@socketio.on('marker_position')
def handle_marker_position(data):
    lat = data['latitude']
    lon = data['longitude']
    print(f"Новые координаты метки: {lat}, {lon}")


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)
