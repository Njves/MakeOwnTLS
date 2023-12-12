from app import app

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run('0.0.0.0:8000', debug=True)
