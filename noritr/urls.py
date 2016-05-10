from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^batcave/', admin.site.urls),
    url(r'^', include('buysell.urls')),
]
