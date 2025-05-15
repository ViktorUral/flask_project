import datetime
import random
import logging
from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from data import db_session
from data.loginform import LoginForm, RegisterForm
from data.users import User
from data_base import get_image_from_db, get_all_cities
from map_utility import get_cords, lonlat_distance

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key_123'
db_session.global_init("db/users.db")

CITY = get_all_cities()


@app.route('/')
def index():
    registered = session.get('registered', None)
    if registered is None:
        session.permanent = True
        session['registered'] = False
        session['city'] = random.choice(CITY)
        session['zoom'] = 14
        session['passed_city'] = []
        session['lat'] = 0
        session['lon'] = 0
    return render_template('index.html', fon=url_for('static', filename='fon.png'))


@app.route('/get_image')
def get_image():
    if not session.get('registered'):
        img_data = get_image_from_db(session['city'], session['zoom'])
    else:
        img_data = get_image_from_db(current_user.city, current_user.zoom)
    return jsonify({'image_data': img_data})


@app.route('/zoom_in', methods=['POST'])
def zoom_in():
    if not session['registered']:
        session['zoom'] = min(session.get('zoom', 14) + 1, 17)
    else:
        zoom = min(current_user.zoom + 1, 17)
        update_user(zoom=zoom)
    return jsonify({'status': 'ok'})


@app.route('/zoom_out', methods=['POST'])
def zoom_out():
    if not session['registered']:
        session['zoom'] = max(session.get('zoom', 14) - 1, 11)
    else:
        zoom = max(current_user.zoom - 1, 11)
        update_user(zoom=zoom)
    return jsonify({'status': 'ok'})


@app.route('/save_position', methods=['POST'])
def save_position():
    data = request.get_json()
    session['lat'] = data['latitude']
    session['lon'] = data['longitude']
    return jsonify({'status': 'ok'})


@app.route('/result')
def result():
    a = request.args.get('a')
    b = request.args.get('b')
    if not session['registered']:
        c, d = get_cords(session['city'])
        session['passed_city'].append(session['city'])
        city = random.choice(CITY)
        while city in session['passed_city']:
            city = random.choice(CITY)
        session['city'] = city
    else:
        c, d = get_cords(current_user.city)
        if lonlat_distance([a, b], [d, c]) <= 250000:
            update_user(city=True, xp=True)
        else:
            update_user(city=True)
    return render_template('result.html',
                           user_cords='[' + a + ',' + b + ']', true_cords='[' + d + ',' + c + ']')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.permanent = True
    session['registered'] = False
    session['city'] = random.choice(CITY)
    session['zoom'] = 14
    session['passed_city'] = []
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            hashed_password=form.password.data,
            city=session.get('city', random.choice(CITY)),
            zoom=session.get('zoom', 14),
            xp=0,
            passed_city=session.get('passed_city', [])
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=False)
        session.pop('name', None)
        session.pop('city', None)
        session.pop('zoom', None)
        session.pop('passed_city', None)
        session['registered'] = True
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


def update_user(zoom=None, city=None, xp=None):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == current_user.name).first()
    if zoom is not None:
        user.zoom = zoom
    if city is not None:
        user.passed_city = user.passed_city + [user.city]
        if len(user.passed_city) == len(CITY):
            user.passed_city = []
        city = random.choice(CITY)
        while city in user.passed_city:
            city = random.choice(CITY)
        user.city = city
    if xp is not None:
        user.xp = user.xp + 1
    db_sess.commit()


if __name__ == '__main__':
    app.run(debug=True)
