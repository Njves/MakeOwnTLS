import random

import flask
from faker import Faker
from flask import render_template, jsonify, request
from app import diffi_helman
from app.models import Cat
from main import app

fake = Faker()


@app.before_request
def send_g_and_p():
    if not flask.session.get('g') or not flask.session.get('p'):
        g, p = diffi_helman.get_g_p()
        flask.session['g'] = g
        flask.session['p'] = p


@app.route('/get', methods=['GET'])
def get_g_and_p():
    return jsonify({'g': flask.session.get('g'), 'p': flask.session.get('p')})

@app.route('/send_key', methods=['POST'])
def send_key():
    A = int(request.json['A'])
    g, p = flask.session.get('g'), flask.session.get('p')
    b = random.randint(10**15, 10**16-1)
    B = pow(g, b, p)
    flask.session['A'] = A
    s_server = pow(A, b, p)
    print(s_server)
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
    if request.form.get('password'):
        print(request.form)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Main page
    """
    return render_template('register.html')
