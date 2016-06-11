import string
import random
import json
import os
from urllib.request import urlopen
from buysell.models import Item, ItemImage
from buysell import keys
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect

def url_coder(size=7, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    url_code = ''.join(random.choice(chars) for _ in range(size))
    while True:
        try:
            i = Item.objects.get(url_code=url_code)
        except Item.DoesNotExist:
            return url_code
        else:
            continue

def ip_finder(ip=keys.IP_KEY):
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


def image_process(images):
    for image in images:
        img_filename = image.name
        img_type = image.content_type
        img_size = len(image)

        # image types are jpg, png, gif
        if img_type == 'image/jpeg' or img_type == 'image/png' or img_type == 'image/gif':
            # image size limited to 5MB or 50M bytes
            if img_size <= 50000000:
                img_name = url_coder(size=11)
                img_ext = os.path.splitext(img_filename)[1].lower()
                img_filename = img_name + img_ext
                img_filepath = os.path.join(settings.MEDIA_ROOT, img_filename)
                default_storage.save(img_filepath, ContentFile(image.read()))

                img_db = ItemImage(title = img_name, location = img_filepath, item=item)
                img_db.save()

            else:
                return HttpResponse('The image is too big')
        else:
            return HttpResponse('Appropriate filetypes are jpg, png, and gif')

def paginator(item_list, page):
    paginator = Paginator(item_list, 24)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        return 1 
    except EmptyPage:
        return 2
    else:
        return items
