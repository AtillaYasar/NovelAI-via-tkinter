# argon_hash and get_access_key are copypasted from Aedial's code, https://github.com/Aedial/novelai-api
# thx bruv.

# installs argon2 if it's not installed yet
import os, sys
try:
    from argon2 import low_level
except ImportError:
    os.system(f'{sys.executable} -m pip install argon2-cffi')
    from argon2 import low_level
from hashlib import blake2b
from base64 import urlsafe_b64encode, b64encode, b64decode
import requests, ast, json

def argon_hash(email: str, password: str, size: int, domain: str) -> str:
    pre_salt = password[:6] + email + domain

    # salt
    blake = blake2b(digest_size = 16)
    blake.update(pre_salt.encode())
    salt = blake.digest()

    raw = low_level.hash_secret_raw(password.encode(), salt, 2, int(2000000/1024), 1, size, low_level.Type.ID)
    hashed = urlsafe_b64encode(raw).decode()

    return hashed

def get_access_key(email: str, password: str) -> str:
    return argon_hash(email, password, 64, "novelai_data_access_key")[:64]

# uses argon_hash and get_access_key to get an authorization key from email and password, which is basically logging in.
def getAuth(email, password):
    accessKey = get_access_key(email, password)
    url = r"https://api.novelai.net/user/login"
    response = requests.request("POST", url, headers={'Content-Type': 'application/json'}, data = json.dumps({'key':accessKey}))

    if response.status_code != 201:
        print(email, password)
        exit('wrong username and/or password')
    
    content = response.content
    decodedContent = content.decode()
    decodedContent = decodedContent.replace("null", "0.0000")
    stringified = ast.literal_eval(decodedContent)
    
    auth = stringified['accessToken']
    print(f'Your authorization key is:\n{auth}') #comment this out if you want..
    return auth

email = 'Jeff_Bezos@goose.honk'
password = 'my_rocket_big_69'
getAuth(email, password)
