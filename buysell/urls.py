from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^gatekeeper/$', views.gatekeeper, name='gatekeeper'),
    url(r'^signup/$', views.sign_up, name='signup'),
    url(r'^login/$', views.log_in, name='login'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^post/create/$', views.post_create, name='post_create'),
    url(r'^post/process/$', views.post_process, name='post_process'),
    url(r'^post/(?P<url_code>\w{7})/$', views.post, name='post'),
    url(r'^list/(?P<area>\w+)/$', views.list, name='list_all'),
    url(r'^list/(?P<area>\w+)/(?P<page>\d+)/$', views.list),
    url(r'^list/(?P<area>\w+)/(?P<category>[-\w]+)/$', views.list, name='list_cat'),
    url(r'^list/(?P<area>\w+)/(?P<category>[-\w]+)/(?P<page>\d+)/$', views.list),
]
