"""
uDisplay/urls.py
Base urls file
Created by Mayank Jain
"""
from django.conf.urls import patterns, include, url
from .views import login_view, logout_view
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/$',  login_view),
    url(r'^logout/$',  logout_view),
    url(r'^',  include('risk_management.urls')),

 #   url(r'^admin/', include(admin.site.urls)),
)
