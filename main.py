from flask import Flask, render_template, request, jsonify
import requests
import base64

app = Flask(__name__)


def get_map_image(point, zoom):
    apikey = "dd4cbcec-5917-4628-8c9b-68567548b81f"  # Замените на ваш ключ
    map_params = {
        "ll": ','.join(point),
        "z": str(zoom),
        "size": "600,400",
        'l': 'map',
        'apikey': apikey  # Добавлен apikey в параметры
    }
    map_api_server = "https://static-maps.yandex.ru/1.x"

    try:
        response = requests.get(map_api_server, params=map_params)
        response.raise_for_status()
        return response.content  # Возвращаем бинарные данные изображения
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе карты: {e}")
        return None


@app.route('/')
def index():
    point = ['37.617644', '55.755826']  # Москва, Кремль
    zoom = 13

    # Получаем изображение карты
    image_data = get_map_image(point, zoom)

    if image_data:
        # Кодируем изображение в base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    else:
        image_base64 = None

    return render_template('map.html', map_image=image_base64)


# API для геокодирования (поиск координат по адресу)
@app.route('/geocode', methods=['POST'])
def geocode():
    address = request.json.get('address')
    if not address:
        return jsonify({"error": "Адрес не указан"}), 400

    # Запрос к API Яндекс.Геокодера
    API_KEY = '8013b162-6b42-4997-9691-77b7074026e0'  # Замените на свой!
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json"

    try:
        response = requests.get(url)
        data = response.json()
        pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        lon, lat = pos.split()
        return jsonify({"lat": lat, "lon": lon})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/save_coords', methods=['POST'])
def save_coords():
    data = request.json
    lat = data['latitude']
    lon = data['longitude']
    print(f"Получены координаты: Широта: {lat}, Долгота: {lon}")
    return jsonify({"status": "success"})


if __name__ == '__main__':
    app.run()
