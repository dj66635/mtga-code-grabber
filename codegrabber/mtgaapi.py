import re
import requests
import json
from constants import MTGA_LOGIN_URL, MTGA_API_LOGIN_URL, MTGA_API_REDEMPTION_URL
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

user_username = config['MTGA']['user_username']
user_password = config['MTGA']['user_password']

def parseCSRFToken(text):
    csrf_pattern = r'_csrf=([a-zA-Z0-9]*)'
    csrf_token = re.search(csrf_pattern, text).group(1)
    return csrf_token
    
def login():
    session = requests.Session()
    response = session.get(MTGA_LOGIN_URL)
    csrf_token = parseCSRFToken(response.headers['Set-Cookie'])
    
    mtgaLogin = {'username': user_username, 'password': user_password, 'remember': 'false', '_csrf': csrf_token}
    response = session.post(MTGA_API_LOGIN_URL, data=json.dumps(mtgaLogin))
    
    response_json = response.json()
    if "error" in response_json:
        raise Exception(f'Error: {response_json["error"]["message"]}')
    elif response.status_code == 200:
        pass
    else:
        raise Exception(f"Failed with status code: {response.status_code}")
        
    return session, csrf_token

def claimCode(session, csrf_token, code):
    payload = {'code': code, '_csrf': csrf_token}
    response = session.post(MTGA_API_REDEMPTION_URL, data=json.dumps(payload))
    
    j = response.json()
    if 'error' in j:
        return j["error"]["message"]
    elif 'data' in j:
        return f'CODE REDEEMED'
    else:
        return f'Unknown response: {j}'
