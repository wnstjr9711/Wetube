from authlib.integrations.base_client import MismatchingStateError
from flask import Flask, render_template, url_for, redirect, session, request, flash
from authlib.integrations.flask_client import OAuth
import pymysql
import requests
import json
import hashlib
import time

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
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/youtube'}
)
accessToken = list()
playlistID = list()
apikey = 'AIzaSyB-9F9Z1JeKt_XH3RbowGsZUTkuLAH7pFs'
available_uchat = ['test201116']
room_created = dict()

# @app.route('/db')
# def show_db():
#     db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='1103', db='service', charset='utf8')
#     cursor = db.cursor()
#     sql = "Select * from test"
#     cursor.execute(sql)
#     result = str(cursor.fetchall())
#     db.close()
#     return result


@app.route('/')
def home():
    if not accessToken:     # session cache clear
        session.clear()
    if session:
        return render_template('html/home/index.html', session=session, code=make_hash())
    else:
        return render_template('html/home/index.html')


@app.route('/movies/<hash_url>')
def movie(hash_url):
    if not session:     # 로그아웃 후 뒤로가기 금지
        return redirect('/')
    if hash_url in room_created:    # 기존 방 입장
        return render_template('html/single-video/single-video-v1.html', uchatroom=room_created[hash_url], session=session)
    if available_uchat:        # 방생성
        u = available_uchat.pop()
        room_created[hash_url] = u
        return render_template('html/single-video/single-video-v1.html', uchatroom=u, session=session, code=make_hash())
    else:                      # uchat 할당 불가
        return redirect(url_for('no_uchat'))


@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/logout')
def logout():
    session.clear()
    accessToken.pop()
    return redirect('/')


@app.route('/authorize')
def authorize():
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        accessToken.append(token['access_token'])
        userinfo = google.get('userinfo').json()
        session['email'] = userinfo['email']
        session['picture'] = userinfo['picture']
    except MismatchingStateError:
        login()
    return redirect('/')


@app.route('/search')
def search():
    url = 'https://www.googleapis.com/youtube/v3/search?key=' + apikey
    req = requests.get(url, {'part': 'snippet', 'q': '파이썬'})
    if req.status_code == 200:
        for i in req.json()['items']:
            print(i['snippet']['title'])
    return redirect('/')


@app.route('/playlist')
def playlist():
    try:
        assert accessToken  # login 상태
        url = 'https://www.googleapis.com/youtube/v3/playlists?access_token=' + accessToken[0]
        req = requests.get(url, {'part': 'snippet', 'mine': 'true'})
        for i in req.json()['items']:
            print(i['id'])
            playlistID.append(i['id'])
        check = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=' + accessToken[0]
        if 'error' in requests.get(check).json(): #access token expired
            return login()
        return redirect('/')
    except (IndexError, AssertionError):
        return login()


@app.route('/playlistItems')
def playlistItems():
    url = 'https://www.googleapis.com/youtube/v3/playlistItems?key=' + apikey
    req = requests.get(url, params={'part': 'snippet', 'playlistId': playlistID[1]})
    print(req.json())
    return redirect('/')


@app.route('/playlistItems_insert')
def playlistItems_insert():
    url = 'https://www.googleapis.com/youtube/v3/playlistItems?access_token=' + accessToken[0]
    req = requests.post(url, params={'part': 'snippet'}, data=json.dumps({'snippet': {'playlistId': 'PLAZnenWndLxcO81kB87Bw-Io4MpHaRPRt', 'resourceId': {'kind': 'youtube#video', 'videoId': 'EAyo3_zJj5c'}}}))
    print(req.status_code)
    return redirect('/')


@app.route('/playlistItems_delete')
def playlistItems_delete():
    url = 'https://www.googleapis.com/youtube/v3/playlistItems?access_token=' + accessToken[0]
    req = requests.delete(url, params={'id': 'UExBWm5lblduZEx4Y084MWtCODdCdy1JbzRNcEhhUlBSdC4yODlGNEE0NkRGMEEzMEQy'})
    print(req.status_code)
    return redirect('/')


@app.route('/join', methods=['GET', 'POST'])
def join_room():
    code = request.form['code']
    return redirect(url_for('movie', hash_url=code))


@app.route('/error_uchat')
def no_uchat():
    return render_template('html/uchatunavailable.html')


def make_hash():
    hash_code = hashlib.sha256(accessToken[0].encode() + str(time.time()).encode())
    return hash_code.hexdigest()


if __name__ == '__main__':
    app.run()
