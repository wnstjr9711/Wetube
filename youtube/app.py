from flask import Flask, render_template, url_for, redirect, session
from authlib.integrations.flask_client import OAuth
import pymysql
import requests
import json

app = Flask(__name__)
app.secret_key = 'random secret'

oauth = OAuth(app)
oauth.register(
    name='google',
    client_id='620470364281-h2os00vpkd6jiel6fq6j4e3on9da9udc.apps.googleusercontent.com',
    client_secret='WO2l5pOnk3wMOO9yChZ0BF4x',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)
accessToken = list()


@app.route('/wnstjr')
def hello_world():
    return render_template('wnstjr.html', data1='김준석', data2='용산', data3=['연희', '연남'])


@app.route('/<user_define>')
def user(user_define):
    return user_define


@app.route('/db')
def show_db():
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1103', db='service', charset='utf8')
    cursor = db.cursor()
    sql = "Select * from test"
    cursor.execute(sql)
    result = str(cursor.fetchall())
    db.close()
    return result


@app.route('/')
def home():
    email = dict(session).get('email', None)
    if accessToken:
        print(accessToken)
    return render_template('html/home/index.html')


@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    accessToken.pop()
    return redirect('/')


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    accessToken.append(token['access_token'])
    # do something with the token and profile
    session['email'] = user_info['email']
    return redirect('/')


@app.route('/search')
def search():
    url = 'https://www.googleapis.com/youtube/v3/search?key=AIzaSyB-9F9Z1JeKt_XH3RbowGsZUTkuLAH7pFs'
    req = requests.get(url, {'part': 'snippet', 'q': '파이썬'})
    if req.status_code == 200:
        for i in req.json()['items']:
            print(i['snippet']['title'])
    return redirect('/')


@app.route('/movies')
def movie():
    return render_template('html/single-video/single-video-v1.html')


if __name__ == '__main__':
    app.run(debug=True)
