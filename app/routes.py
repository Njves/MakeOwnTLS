import random

import flask
from faker import Faker
from flask import render_template, jsonify, request

from app import diffi_helman
from app.diffi_helman import hash_key
from app.models import Cat
from main import app

fake = Faker()

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


@app.route('/send_key', methods=['POST'])
def send_key():
    """
    Получает на вход открытый ключ клиента создает закрытый ключ
    собирает открытый ключ и его отправляет клиенту
    :return:
    """
    A = int(request.json['A'])
    g, p = flask.session.get('g'), flask.session.get('p')
    b = diffi_helman.secret_key_server()
    B = diffi_helman.get_shared_client_key(g, b, p)
    flask.session['A'] = A
    s_server = diffi_helman.get_shared_server_key(A, b, p)
    flask.session['s_server'] = s_server
    return jsonify({'B': B})


@app.route('/', methods=['GET'])
def index():
    """
    Main page
    """
    cats = Cat.query.all()
    return render_template('index.html', cats=cats)


@app.route('/add', methods=['GET'])
def add():
    """
    Main page
    """
    return render_template('insert.html')


@app.route('/add', methods=['POST'])
def add_cat():
    """
    Main page
    """
    return render_template('insert.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Main page
    """
    if request.method == 'POST':
        print(request.json)
        print(flask.session['s_server'])
        user_login = request.json['username']
        password = request.json['password']
        iv = request.json['iv']
        key = flask.session['s_server']
        key_hash = hash_key(key)
        if user_login and password and iv:
            password = diffi_helman.decrypt(password, key_hash, iv)
            print(password)
            return jsonify({'ok': 'ok'})

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Main page
    """
    return render_template('register.html')
