from django import template
from django.conf import settings as base_set
from buysell.models import Category, Message
from django.utils.dateformat import format
import time

register = template.Library()

@register.simple_tag
def gmaps():
    keys = base_set.GMAPS_KEY
    return keys

@register.simple_tag
def get_cats():
    cats = Category.objects.all().order_by('kor_name')
    return cats

@register.filter
def new_item(pub_date):
    cur_time = time.time()
    pub_time = format(pub_date, 'U')

    dif_time = int(cur_time) - int(pub_time)

    if dif_time <= 86400:
       return True
    else:
        return False

@register.filter
def inbox(url_code):
    msg = Message.objects.filter(url_code=url_code).latest('pub_date')
    return msg

@register.filter
def is_read(url_code):
    try:
        is_read = Message.objects.filter(url_code=url_code, is_read=False).last().sender.username
    except:
        is_read = None
    return is_read

@register.filter
def total_msg(user):
    total = Message.objects.filter(recipient=user).all().count()
    return total

@register.filter
def unread_msg(user):
    unread = Message.objects.filter(recipient=user, is_read=False).all().count()
    return unread

@register.filter
def sent_msg(user):
    sent = Message.objects.filter(sender=user).count()
    return sent

@register.simple_tag
def img_url():
    url = base_set.MEDIA_URL
    return url

@register.simple_tag
def thumb_url():
    url = base_set.MEDIA_URL + 'thumb_'
    return url
