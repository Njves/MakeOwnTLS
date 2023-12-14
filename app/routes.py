import flask
from flask import render_template, jsonify, request, redirect, url_for, make_response, Response
from werkzeug.local import LocalProxy

from app import diffi_helman, db
from app.diffi_helman import hash_key
from app.models import Cat, User, Role
from main import app

current_user = LocalProxy(lambda: User.query.filter_by(id=flask.session.get('user_id')).first())


@app.before_request
def make_session_permanent():
    global current_user
    if not Role.query.filter_by(name='Пользователь').first():
        role = Role(name='Пользователь')
        role1 = Role(name='Админ')
        db.session.add(role)
        db.session.add(role1)
        db.session.commit()
    current_user = LocalProxy(lambda: User.query.filter_by(id=flask.session.get('user_id')).first())

    flask.session.get('user_id')
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
    return dict(user=current_user if current_user else False)


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


def encrypt_view(template):
    cipher, iv = diffi_helman.encrypt(template, hash_key(flask.session['s_server']))
    return jsonify({'html': cipher, 'iv': iv})


@app.route('/cipher', methods=['GET'])
def index_cipher():
    """
    Главная страница
    """
    cats = Cat.query.all()
    return encrypt_view(render_template('index.html', cats=cats))

@app.route('/', methods=['GET'])
def index():
    """
    Главная страница
    """
    return render_template('index_cipher.html')




@app.route('/add', methods=['GET'])
def add():
    """
    Форма добавления котят
    """
    if not flask.session.get(app.config['USER_FIELD']):
        return redirect(url_for('login'))
    return render_template('add_cipher.html')


@app.route('/add_cipher', methods=['GET'])
def add_cipher():
    """
    Форма добавления котят
    """
    if not flask.session.get(app.config['USER_FIELD']):
        return redirect(url_for('login'))
    return encrypt_view(render_template('insert.html'))


@app.route('/add', methods=['POST'])
def add_cat():
    """
    Ручка для добавления котят
    """
    if not request.json:
        return redirect(url_for('add'))
    name = request.json['name']
    desc = request.json['description']
    breed = request.json['breed']
    link = request.json['link']
    photo_link = request.json['photo_link']
    iv = request.json['iv']
    key = flask.session['s_server']
    key_hash = hash_key(key)
    if iv:
        name = diffi_helman.decrypt(name, key_hash, iv)
        desc = diffi_helman.decrypt(desc, key_hash, iv)
        breed = diffi_helman.decrypt(breed, key_hash, iv)
        link = diffi_helman.decrypt(link, key_hash, iv)
        photo_link = diffi_helman.decrypt(photo_link, key_hash, iv)
        cat = Cat(name=name, description=desc, breed=breed, link=link, photo_link=photo_link)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('index'))
    return redirect(url_for('add'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ручка логина
    """
    if current_user:
        return redirect(url_for('index'))
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
        print(request.json)
        if user_login and password and iv:
            username = diffi_helman.decrypt(user_login, key_hash, iv)
            password = diffi_helman.decrypt(password, key_hash, iv)
            user = User.query.filter_by(username=username).first()
            if user is None:
                return Response(status=404)
            if not user.check_password(password):
                return Response(status=401)
            flask.session[app.config['USER_FIELD']] = user.id
            print(flask.session[app.config['USER_FIELD']])
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    if flask.session.get(app.config['USER_FIELD']):
        flask.session.pop(app.config['USER_FIELD'])
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Ручка регистрации
    """
    if current_user:
        return redirect(url_for('index'))
    print(request.json)
    if request.method == 'POST':
        if not request.json:
            return redirect(url_for('register'))
        user_login = request.json['username']
        password = request.json['password']
        admin = request.json['has_admin']
        iv = request.json['iv']
        key = flask.session['s_server']
        key_hash = hash_key(key)
        print(request.json)
        if user_login and password and iv:
            username = diffi_helman.decrypt(user_login, key_hash, iv)
            password = diffi_helman.decrypt(password, key_hash, iv)
            has_admin = diffi_helman.decrypt(admin, key_hash, iv)
            if User.query.filter_by(username=username).first():
                return Response(status=406)
            user = User(username=username)
            if has_admin == 'true':
                user.role = Role.query.filter_by(name='Админ').first()
            else:
                user.role = Role.query.filter_by(name='Пользователь').first()

            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flask.session[app.config['USER_FIELD']] = User.query.filter_by(username=username).first().id
            return redirect(url_for('index'))
    text, iv = diffi_helman.encrypt(render_template('register.html'), flask.session['s_server'].to_bytes(16, 'little'))
    html = diffi_helman.decrypt(text, flask.session['s_server'].to_bytes(16, 'little'), iv)
    print(html)
    return render_template('register.html')


@app.route('/delete', methods=['POST'])
def delete():
    if not request.json:
        return redirect(url_for('index'))
    if not current_user:
        return redirect(url_for('login'))
    if current_user.role.name != 'Админ':
        return redirect(url_for('index'))
    iv = request.json['iv']
    key = flask.session['s_server']
    key_hash = hash_key(key)
    cat_id = diffi_helman.decrypt(request.json['cat_id'], key_hash, iv)
    db.session.delete(Cat.query.filter_by(id=cat_id).first())
    db.session.commit()
    return redirect(url_for('index'))
