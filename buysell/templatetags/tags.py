from django import template
from buysell.models import Category

register = template.Library()

@register.simple_tag
def get_cats():
    cats = Category.objects.all().order_by('kor_name')
    return cats

