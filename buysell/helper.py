import string
import random
from buysell.models import Item

def url_coder(size=7, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    url_code = ''.join(random.choice(chars) for _ in range(size))
    while True:
        try:
            i = Item.objects.get(url_code=url_code)
        except Item.DoesNotExist:
            return url_code
        else:
            continue
