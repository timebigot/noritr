from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup', views.sign_up, name='signup'),
    url(r'^login', views.log_in, name='login'),
    url(r'^logout', views.log_out, name='logout'),
    url(r'^create', views.create_post, name='create_post'),
    url(r'^process_post', views.process_post, name='process_post'),
]
