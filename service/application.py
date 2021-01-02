import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from authlib.integrations.base_client import MismatchingStateError
from flask import Flask, render_template, url_for, redirect, session, request
from authlib.integrations.flask_client import OAuth
import requests
import json
import hashlib
import time
import dbconnect
import random


application = Flask(__name__)
application.secret_key = 'random secret'
oauth = OAuth(application)
oauth.register(
    name='google',
    client_id='727864232274-r8asqou7pjj31rdc8295gh1u82c0egfe.apps.googleusercontent.com',
    client_secret='9jg-Riv-k8uTSGYfTk-q01n5',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/youtube '
                            'https://www.googleapis.com/auth/gmail.send '
                            'https://mail.google.com '}
)
apikey = 'AIzaSyDbcAEKDdjQJyCRDdvxa2e7vebtUZnb790'
available_uchat = ['SO_9_1', 'SO_9_2', 'SO_9_3']


@application.route('/')
def home():
    if 'token' in session:
        if check_token():
            return render_template('html/home/index.html', session=session, code=make_hash())
        else:
            return render_template('html/home/index.html', session=session, code='None')
    else:
        return render_template('html/home/index.html', session=session, code='None')


@application.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@application.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@application.route('/authorize')
def authorize():
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        userinfo = google.get('userinfo').json()
        session['email'] = userinfo['email']
        session['picture'] = userinfo['picture']
        session['token'] = token['access_token']
        session['name'] = userinfo['name']
    except MismatchingStateError:
        login()
    return redirect('/')


@application.route('/movies/<hash_url>')
def movie(hash_url):
    if not session:     # 로그아웃 후 뒤로가기 금지
        return redirect('/')
    check_token()
    rooms = dbconnect.get_rooms()
    if hash_url in rooms:    # 기존 방 입장
        uid = rooms[hash_url]
        return render_template('html/single-video/video.html', uchatroom=uid, session=session, code=make_hash(),
                               playlists=dbconnect.get_playlists(uid), play=dbconnect.get_playlist(uid),
                               items=dbconnect.get_videos(uid), selected=dbconnect.get_video(uid),
                               search=session.pop('search') if 'search' in session else None)
    else:        # 방생성
        # uid = available_uchat.pop()
        uid = available_uchat[random.randint(0, 2)]
        playlists = get_playlist()
        dbconnect.create_roomTest(uid, hash_url, playlists)
        # dbconnect.create_room(uid, hash_url, playlists)
        return render_template('html/single-video/video.html', uchatroom=uid, session=session,
                               code=make_hash(), playlists=playlists, play=None)


@application.route('/join', methods=['GET', 'POST'])
def join_room():
    code = request.form['code']
    return redirect(url_for('movie', hash_url=code))


@application.route('/change_playlist', methods=['GET', 'POST'])
def change_playlist():
    url = request.args['url'].split('/')[-1]
    uid = dbconnect.get_rooms()[url]
    if 'playlist' in request.form:
        pl = request.form['playlist']  # 'id'
        pli = get_playlistItems(pl)
        if type(pli) is list:  # 빈 playlist의 경우도 가져옴
            dbconnect.set_playlist(uid, pl)
            dbconnect.set_videos(uid, pli)
    if 'select' in request.args:
        dbconnect.set_video(uid, eval(request.args['select']))
    return redirect(url_for('movie', hash_url=url))


@application.route('/search', methods=['GET', 'POST'])
def search():
    code = request.args['url'].split('/')[-1]
    url = 'https://www.googleapis.com/youtube/v3/search?key=' + apikey
    req = requests.get(url, {'part': 'snippet', 'maxResults': 10, 'q': request.form['search_video']})
    result = req.json()['items']
    for i in result:
        i['snippet']['title'] = i['snippet']['title'].replace('&#39;', '\'')
        i['snippet']['title'] = i['snippet']['title'].replace('&quot;', '"')
        i['snippet']['title'] = i['snippet']['title'].replace('&#34;', '"')
        i['snippet']['title'] = i['snippet']['title'].replace('&#38;', '&')
        i['snippet']['title'] = i['snippet']['title'].replace('&amp;', '&')
        i['snippet']['title'] = i['snippet']['title'].replace('&nbsp;', ' ')
    if req.status_code == 200:
        session['search'] = result
    return redirect(url_for('movie', hash_url=code))


@application.route('/add', methods=['GET', 'POST'])
def add():
    code = request.args['url'].split('/')[-1]
    uid = dbconnect.get_rooms()[code]
    url = 'https://www.googleapis.com/youtube/v3/playlistItems?access_token=' + session['token']
    pl = dbconnect.get_playlist(uid)
    result = list()
    for i in request.form:
        if eval(i) not in [i['snippet']['resourceId'] for i in dbconnect.get_videos(uid)]:
            req = requests.post(url, params={'part': 'snippet'},
                                data=json.dumps({'snippet': {'playlistId': pl, 'resourceId': eval(i)}}))
            if req.status_code == 403:
                break
            result.append(req.json())
    dbconnect.set_videos(uid, result)
    return redirect(url_for('movie', hash_url=code))


@application.route('/send', methods=['GET', 'POST'])
def send():
    code = request.args['url']
    sendmail(session['email'], request.form['send'], session['name']+'님의 초대코드', code)
    return redirect(url_for('movie',  hash_url=code.split('/')[-1]))


# Gmail 보내기
@application.route('/send_mail')
# Message 생성 함수
def CreateMessage(sender, to, subject, message_text):
    """Create a message for an email.
    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        attachment_path: Full path for attachment (dir+filename)
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    if message_text is not None:
        msg = MIMEText(message_text, 'html')
        message.attach(msg)
    try:
        return {'raw': base64.urlsafe_b64encode(message.as_string())}
    except:
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf8')}


# Message 전송 함수
def sendmail(host, to, subject, message_text_html):
    url = 'https://www.googleapis.com/gmail/v1/users/' + host + '/messages/send'
    request_header = {"Content-Type": "application/json",
                      "Authorization": "Bearer " + session['token'],
                      "X-GFE-SSL": "yes"
                      }
    message_text_html = message_text_html + '<br><br>code: ' + message_text_html.split('/')[-1]
    payload = CreateMessage(host, to, subject, message_text_html)
    return requests.post(url, headers=request_header, data=json.dumps(payload))


def get_playlist():  # 사용자 playlist 가져오기(없는경우 임의로 생성)
    url = 'https://www.googleapis.com/youtube/v3/playlists?access_token=' + session['token']
    req = requests.get(url, {'part': 'snippet', 'mine': 'true'})
    while 'items' not in req.json():
        req = requests.get(url, {'part': 'snippet', 'maxResults': 20, 'mine': 'true'})
    result = req.json()['items']
    if not result:
        url2 = 'https://www.googleapis.com/youtube/v3/playlists?access_token=' + session['token']
        req2 = requests.post(url2, params={'part': 'snippet'}, data=json.dumps({'snippet': {
            'title': 'new'}}))
        result.append(req2.json())
    return result


def get_playlistItems(playlist):
    url = 'https://www.googleapis.com/youtube/v3/playlistItems?access_token=' + session['token']
    req = requests.get(url, params={'part': 'snippet', 'maxResults': 50, 'playlistId': playlist})
    if req.status_code == 404:  # playlist의 host가 아닌경우 가져올 수 없음
        return None
    while 'items' not in req.json():
        req = requests.get(url, params={'part': 'snippet', 'playlistId': playlist})
    return req.json()['items']


def make_hash():
    hash_code = hashlib.sha256(session['token'].encode() + str(time.time()).encode())
    return hash_code.hexdigest()


def check_token():
    check = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=' + session['token']
    if 'error' in requests.get(check).json():  # access token expired
        logout()
        return False
    else:
        return True


if __name__ == "__main__":
    application.run(host="0.0.0.0")
