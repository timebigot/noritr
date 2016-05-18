from django import template
from buysell.models import Area, Category

register = template.Library()

@register.simple_tag
def get_areas():
    areas = Area.objects.all()
    return areas

@register.simple_tag
def get_cats():
    cats = Category.objects.all()
    return cats

