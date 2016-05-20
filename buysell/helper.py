import string
import random
import json
from urllib.request import urlopen
from buysell.models import Item
from buysell import keys

def url_coder(size=7, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    url_code = ''.join(random.choice(chars) for _ in range(size))
    while True:
        try:
            i = Item.objects.get(url_code=url_code)
        except Item.DoesNotExist:
            return url_code
        else:
            continue

def ip_finder(ip=keys.IP):
    url = 'http://api.ipinfodb.com/v3/ip-city/?key=' + keys.IP_KEY + '&format=json&ip=' + ip
    res = urlopen(url).read().decode('utf-8')
    obj = json.loads(res)

    state = obj['regionName']

    return state

def get_ip():

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip
