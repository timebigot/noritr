from django.contrib import admin
from .models import *

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('eng_name',)}

admin.site.register(UserProfile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Area)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Item)
admin.site.register(ItemImage)
