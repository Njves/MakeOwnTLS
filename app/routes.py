import flask
from flask import render_template, jsonify, request, redirect, url_for, make_response, flash, Response

from app import diffi_helman, db
from app.diffi_helman import hash_key
from app.models import Cat, User
from main import app


@app.before_request
def make_session_permanent():
    flask.session.permanent = True

@app.route('/get', methods=['GET'])
def get_g_and_p():
    """
    Ручка выдающая значения g, p
    :return:
    """
    g, p = diffi_helman.get_g_p()
    flask.session['g'] = g
    flask.session['p'] = p
    return jsonify({'g': g, 'p': p})


@app.context_processor
def inject_user():
    """
    Внедряет поле пользователя в Jinja если пользователь авторизован
    :return:
    """
    user = User.query.filter_by(id=flask.session.get('user_id')).first()
    return dict(user=user if user else False)


@app.route('/send_key', methods=['POST'])
def send_key():
    """
    Получает на вход открытый ключ клиента создает закрытый ключ
    собирает открытый ключ и его отправляет клиенту
    :return:
    """
    A = int(request.json['A'])
    flask.session['A'] = A
    g, p = flask.session.get('g'), flask.session.get('p')
    b = diffi_helman.secret_key_server()
    B = diffi_helman.get_shared_client_key(g, b, p)
    s_server = diffi_helman.get_shared_server_key(A, b, p)
    flask.session['s_server'] = s_server
    return jsonify({'B': B})


@app.route('/', methods=['GET'])
def index():
    """
    Главная страница
    """
    cats = Cat.query.all()
    return render_template('index.html', cats=cats)


@app.route('/add', methods=['GET'])
def add():
    """
    Форма добавления котят
    """
    return render_template('insert.html')


@app.route('/add', methods=['POST'])
def add_cat():
    """
    Ручка для добавления котят
    """
    return render_template('insert.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ручка логина
    """
    if request.method == 'POST':
        if not request.json:
            return redirect(url_for('register'))
        if flask.session.get(app.config['USER_FIELD']):
            return redirect(url_for('index'))
        user_login = request.json['username']
        password = request.json['password']
        iv = request.json['iv']
        key = flask.session['s_server']
        key_hash = hash_key(key)
        if user_login and password and iv:
            username = diffi_helman.decrypt(user_login, key_hash, iv)
            password = diffi_helman.decrypt(password, key_hash, iv)
            user = User.query.filter_by(username=username).first()
            if not user:
                flash('Такого пользователя не существует')
                return redirect(url_for('login'))
            user = User.query.filter_by(username=username).first()
            if not user.check_password(password):
                flash('Неверный пароль')
                return redirect(url_for('login'))
            flask.session[app.config['USER_FIELD']] = user.id
            return jsonify({'user': user.username})
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    flask.session.pop(app.config['USER_FIELD'])
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Ручка регистрации
    """
    if request.method == 'POST':
        if not request.json:
            return redirect(url_for('register'))
        user_login = request.json['username']
        password = request.json['password']
        iv = request.json['iv']
        key = flask.session['s_server']
        key_hash = hash_key(key)
        if user_login and password and iv:
            username = diffi_helman.decrypt(user_login, key_hash, iv)
            password = diffi_helman.decrypt(password, key_hash, iv)
            if User.query.filter_by(username=username).first():
                flash('Пользователь уже существует')
                return redirect(url_for('register'))
            user = User(username=username)
            user.set_password(password)
            flask.session['user_id'] = user.id
            flash('Вы зарегестрировались')
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('register.html')
