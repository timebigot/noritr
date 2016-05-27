from django.conf.urls import url, include, patterns
from . import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^join', views.join, name='join'),
    url(r'^signup/$', views.sign_up, name='signup'),
    url(r'^login/$', views.log_in, name='login'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^change_zip/$', views.change_zip, name='change_zip'),
    url(r'^search/$', views.search, name='search'),
    url(r'^post/create/$', views.post_create, name='post_create'),
    url(r'^post/process/$', views.post_process, name='post_process'),
    url(r'^post/(?P<url_code>\w{7})/$', views.post, name='post'),
    url(r'^list/(?P<category>[-\w]+)/$', views.list, name='list_cat'),
    url(r'^list/(?P<category>[-\w]+)/(?P<page>\d+)/$', views.list, name='list_cat_page'),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('', (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))
