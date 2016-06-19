from django.conf.urls import url, include, patterns
from . import views
from django.conf import settings

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^join', views.join, name='join'),
    url(r'^signup/$', views.sign_up, name='signup'),
    url(r'^login/$', views.log_in, name='login'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^change_zip/$', views.change_zip, name='change_zip'),
    url(r'^search/$', views.search, name='search_redirect'),
    url(r'^search/(?P<query>[^\/]+)/$', views.search, name='search'),
    url(r'^search/(?P<query>[^\/]+)/(?P<page>\d+)/$', views.search, name='search_page'),
    url(r'^post/create/$', views.post_create, name='post_create'),
    url(r'^post/remove/$', views.post_remove, name='post_remove'),
    url(r'^post/edit/(?P<url_code>\w+)/$', views.post_edit, name='post_edit'),
    url(r'^post/repost/(?P<url_code>\w+)/$', views.post_repost, name='post_repost'),
    url(r'^post/process/$', views.post_process, name='post_process'),
    url(r'^post/(?P<url_code>\w{7})/$', views.post, name='post'),
    url(r'^list/(?P<category>[-\w]+)/$', views.list, name='list_cat'),
    url(r'^list/(?P<category>[-\w]+)/(?P<page>\d+)/$', views.list, name='list_cat_page'),
    url(r'^message/$', views.message, name='message'),
    url(r'^inbox/$', views.inbox, name='inbox'),
    url(r'^inbox/(?P<url_code>\w+)/$', views.inbox, name='thread'),
    url(r'^bot/$', views.bot, name='bot'),
    url(r'^store/manage/$', views.store_manage, name='store_manage'),
    url(r'^store/(?P<seller>[^\/]+)/$', views.store, name='store'),
    url(r'^store/(?P<seller>[^\/]+)/(?P<page>\d+)/$', views.store, name='store_page'),
    url(r'^history/$', views.history, name='history'),
    url(r'^history/(?P<page>\d+)/$', views.history, name='history_page'),
    url(r'^favorites/$', views.favorites, name='favorites'),
    url(r'^favorites/(?P<page>\d+)/$', views.favorites, name='favorites_page'),
]

if settings.DEBUG:
    urlpatterns += patterns('', (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))
else:
    print('Production!')
