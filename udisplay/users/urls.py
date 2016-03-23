# Third Party Stuff
from django.conf.urls import url
from django.contrib.auth import views as dj_auth_views

from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^login/$', views.login, name="login"),
    url(r'^logout/$', dj_auth_views.logout_then_login, name="logout"),
]
