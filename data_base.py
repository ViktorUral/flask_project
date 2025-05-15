from data.db_session import global_init, create_session
from data.map import Map
from data.admin import Admin
from passlib.hash import bcrypt
from map_utility import get_cords, get_response_as_base64

# Инициализация БД
global_init("db/maps.db")


def verify_admin_password(password):
    session = create_session()
    try:
        admin = session.query(Admin).get(1)
        return admin and bcrypt.verify(password, admin.password_hash)
    finally:
        session.close()


def save_to_db(city, zoom, image_data):
    session = create_session()
    try:
        map_entry = Map(
            city=city,
            zoom=zoom,
            image_data=image_data
        )
        session.add(map_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_cities():
    session = create_session()
    try:
        return [city[0] for city in session.query(Map.city).distinct().all()]
    finally:
        session.close()


def get_image_from_db(city, zoom):
    session = create_session()
    try:
        result = session.query(Map.image_data).filter(
            Map.city == city,
            Map.zoom == zoom
        ).first()
        return result[0] if result else None
    finally:
        session.close()


def add_map_data(password, name):
    if not verify_admin_password(password):
        print("Неверный пароль администратора!")
        return

    coords = get_cords(name)
    for zoom in range(11, 18):
        image_base64 = get_response_as_base64(coords, zoom)
        if image_base64:
            save_to_db(name, zoom, image_base64)
            print(f"Данные для {name} (zoom {zoom}) сохранены!")
