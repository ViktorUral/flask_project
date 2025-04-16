from flask import Flask, render_template, url_for, redirect, request
from flask_socketio import SocketIO, emit
import io
import base64
import random
import requests
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app)
zoom = 15
logging.basicConfig(
    filename='/home/simpleproject/error.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.ERROR
)
cities_over_8m = [
    "Токио", "Дели", "Шанхай", "Пекин", "Сеул",

    "Каир", "Мехико", "Нью-Йорк", "Лос-Анджелес",

    "Сан-Паулу", "Буэнос-Айрес", "Рио-де-Жанейро",
    "Москва", "Стамбул"
]
city_num = random.randint(0, len(cities_over_8m) - 1)
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
        logging.error(e)


def generate_map_image(cords, zoom):
    binary_data = get_response(cords, zoom)
    img_str = base64.b64encode(binary_data.content).decode("utf-8")
    return img_str


# Главная страница
@app.route('/')
def index():
    return render_template('index.html', fon=url_for('static', filename='fon.png'))


# Обработчик WebSocket-запроса на обновление изображения
@socketio.on('request_plus_image')
def handle_image_request():
    global zoom, city_num
    img_data = generate_map_image(get_cords(cities_over_8m[city_num]), zoom)
    emit('update_image', {'image_data': img_data})
    zoom += 1
    if zoom < 17:
        zoom += 1
    else:
        zoom = 17


@socketio.on('request_dif_image')
def handle_image_request():
    global zoom, city_num
    img_data = generate_map_image(get_cords(cities_over_8m[city_num]), zoom)
    emit('update_image', {'image_data': img_data})
    if zoom > 11:
        zoom -= 1
    else:
        zoom = 11


@socketio.on('marker_position')
def handle_marker_position(data):
    global lat, lon
    lat = data['latitude']
    lon = data['longitude']


@socketio.on('result_map')
def handle_marker_position():
    global lat, lon, city_num
    city_num = random.randint(0, len(cities_over_8m) - 1)
    emit('redirect_to_result', {'a': lat, 'b': lon})


@app.route('/result')
def result():
    a = request.args.get('a')
    b = request.args.get('b')
    c, d = get_cords(cities_over_8m[city_num])
    return render_template('result.html', fon=url_for('static', filename='fon.png'),
                           user_cords='[' + a + ',' + b + ']', true_cords='[' + d + ',' + c + ']')

# if __name__ == '__main__':
#    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)
