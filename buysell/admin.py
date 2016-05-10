from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Area)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Item)
admin.site.register(ItemImage)
