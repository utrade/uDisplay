"""
urls for risk_management app.

risk_management/urls.py
Created by Mayank Jain
"""

from django.conf.urls import patterns, include, url
from .views import accounts, save_account_ids

urlpatterns = patterns('',
    url(r'^$',  accounts),
    url(r'^save_accounts/$', save_account_ids),
)
