from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('eng_name',)}

class AreaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'customer'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (CustomerInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Customer)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Item)
admin.site.register(ItemImage)
admin.site.register(PostView)
admin.site.register(Zipcode)
admin.site.register(Message)
