import json
import requests

url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

redirect_url = 'https://www.naver.com'
app_key = '0643fa6a2a932776c78ca3dafff00fbe'
access_token = ''
oauth_url = 'https://kauth.kakao.com/oauth/authorize?client_id='+app_key+'&redirect_uri='+redirect_url+'&response_type=code'
# template_object = { "object_type": "text", "text": "msg", "link":}

print(oauth_url)