from flask import Flask, render_template, url_for, redirect, request
from flask_socketio import SocketIO, emit
import io
import base64
import random
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app)
zoom = 15
CITY = ['Кейптаун', 'Москва', 'Нью-Йорк', 'Париж', 'Сидней', 'Токио']
COORDS = [
    [-33.9249, 18.4241],
    [-33.8688, 151.2093],
    [55.7558, 37.6176],
    [40.7128, -74.0060],
    [48.8566, 2.3522],
    [35.6762, 139.6503]
]
city_num = -1
lat, lon = 0, 0


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
def generate_map_image(zoom, image):
    with open(image, "rb") as file:
        binary_data = file.read()
    img_str = base64.b64encode(binary_data).decode("utf-8")
    return img_str


# Главная страница
@app.route('/')
def index():
    return render_template('index.html', fon=url_for('static', filename='fon.png'))


# Обработчик WebSocket-запроса на обновление изображения
@socketio.on('request_plus_image')
def handle_image_request():
    global zoom, CITY, city_num
    img_data = generate_map_image(zoom, f'static/{zoom}/{CITY[city_num]}.png')
    emit('update_image', {'image_data': img_data})
    zoom += 1
    if zoom < 17:
        zoom += 1
    else:
        zoom = 17


@socketio.on('request_dif_image')
def handle_image_request():
    global zoom, CITY, city_num
    img_data = generate_map_image(zoom, f'static/{zoom}/{CITY[city_num]}.png')
    emit('update_image', {'image_data': img_data})
    if zoom > 12:
        zoom -= 1
    else:
        zoom = 12


@socketio.on('marker_position')
def handle_marker_position(data):
    global lat, lon
    lat = data['latitude']
    lon = data['longitude']


@socketio.on('result_map')
def handle_marker_position():
    global lat, lon, city_num, COORDS
    if city_num != 5:
        city_num += 1
    else:
        city_num = 0
    print(COORDS[city_num][0], COORDS[city_num][1])
    emit('redirect_to_result', {'a': lat, 'b': lon})


@app.route('/result')
def result():
    global COORDS
    a = request.args.get('a')
    b = request.args.get('b')
    c = str(COORDS[city_num][0])
    d = str(COORDS[city_num][1])
    return render_template('result.html', fon=url_for('static', filename='fon.png'),
                           user_cords='[' + a + ',' + b + ']', true_cords='[' + c + ',' + d + ']')


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)
