import requests
from pprint import pprint
from urllib.parse import urlencode

APP_ID = 7058950

URL = 'https://oauth.vk.com/authorize'

def gettoken():
    # ACC_TOKEN = 'a4541a46101a30b5b599dac3e32458db2f6732e0b8dd9e01870e7b532a8a289ccee36259cc5e32341a4cb' # friends, offline. old delete app
    ACC_TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1' # from netology
    # ACC_TOKEN = '357334a1a2a05d2e55b7ae14f4797323bb0520e12871c5a511aa76f19d3414ed053ab2c60a6e18f56e8f5' # friends, offline
    # ACC_TOKEN = '164f9bc4e724e0caa7b636bf8f6e78c385a69f83364be0cd7cdccecebf6751751bc47309dbbc140c1e99f' # friends, group, offline
    # ACC_TOKEN = 'be427a11b7c20f57643d8c52d87e5f357ad196f90e59d5752449fa46f015104781de59787f9706b18aac2' # group, offline
    return ACC_TOKEN

params = {
    'client_id': APP_ID,
    'display': 'page',
    'scope': 'friends groups offline',
    'response_type': 'token'
}

if __name__ == '__main__':
    print('?'.join((URL, urlencode(params))))

# offline

# print('?'.join((URL, urlencode(params))))


# 'https://oauth.vk.com/blank.html#access_token=41805767e2d6116e91266eb2c84d6b4eb5db461e497886479e4c13b5d9d2c568c08400e199bbf42badb1e&expires_in=86400&user_id=10554929'

# 'https://oauth.vk.com/blank.html#access_token=a4541a46101a30b5b599dac3e32458db2f6732e0b8dd9e01870e7b532a8a289ccee36259cc5e32341a4cb&expires_in=0&user_id=10554929'

# https://oauth.vk.com/blank.html#access_token=164f9bc4e724e0caa7b636bf8f6e78c385a69f83364be0cd7cdccecebf6751751bc47309dbbc140c1e99f&expires_in=0&user_id=10554929
# https://oauth.vk.com/blank.html#access_token=357334a1a2a05d2e55b7ae14f4797323bb0520e12871c5a511aa76f19d3414ed053ab2c60a6e18f56e8f5&expires_in=0&user_id=10554929
# https://oauth.vk.com/blank.html#access_token=be427a11b7c20f57643d8c52d87e5f357ad196f90e59d5752449fa46f015104781de59787f9706b18aac2&expires_in=0&user_id=10554929