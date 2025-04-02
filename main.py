from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# Главная страница с картой
@app.route('/')
def index():
    return render_template('map.html')


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


if __name__ == '__main__':
    app.run()
