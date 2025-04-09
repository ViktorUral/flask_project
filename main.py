from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

zoom = 12
current_location = "Москва"

# Храним последние координаты
last_coords = [55.751244, 37.618423]


@app.route('/')
def index():
    return render_template('map.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/geocode', methods=['POST'])
def geocode():
    address = request.json.get('address')
    if not address:
        return jsonify({"error": "Адрес не указан"}), 400

    API_KEY = 'your_yandex_api_key'
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json"

    try:
        response = requests.get(url)
        data = response.json()
        pos = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        lon, lat = pos.split()
        global last_coords, current_location
        last_coords = [float(lat), float(lon)]
        current_location = address
        emit('map_update', {'coords': last_coords, 'zoom': zoom, 'location': current_location}, broadcast=True)
        return jsonify({"lat": lat, "lon": lon})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/save_coords', methods=['POST'])
def save_coords():
    data = request.json
    global last_coords, zoom
    last_coords = [data['latitude'], data['longitude']]
    zoom = data.get('zoom', 12)
    emit('map_update', {'coords': last_coords, 'zoom': zoom}, broadcast=True)
    return jsonify({"status": "success"})


@socketio.on('request_map')
def handle_map_request():
    emit('map_update', {
        'coords': last_coords,
        'zoom': zoom,
        'location': current_location,
        'image_url': f'/static/maps/{zoom}/{current_location}.png'
    })


@socketio.on('zoom_change')
def handle_zoom_change(data):
    global zoom
    zoom += data.get('delta', 0)
    zoom = max(10, min(20, zoom))
    emit('map_update', {
        'coords': last_coords,
        'zoom': zoom,
        'location': current_location,
        'image_url': f'/static/maps/{zoom}/{current_location}.png'
    }, broadcast=True)


if __name__ == '__main__':
    if not os.path.exists('static/maps'):
        os.makedirs('static/maps')
    socketio.run(app, debug=True)
