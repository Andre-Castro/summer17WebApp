from django.conf.urls import url
from . import views

urlpatterns = [
	# url(r'$', views.index, name='index'),	
    url(r'(?P<forum>[a-zA-Z-_]+)/ip/(?P<page>[0-9]+)/$', views.ip_list),
    url(r'(?P<forum>[a-zA-Z-_]+)/ip/$', views.ip_list),
	url(r'(?P<forum>[a-zA-Z-_]+)/user/$', views.user),
    url(r'(?P<forum>[a-zA-Z-_]+)/extra/$', views.extra),
    url(r'(?P<forum>[a-zA-Z-_]+)/$', views.index),
]