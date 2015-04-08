"""
Database setup for uDisplay project.

risk_management/models.py
Created by Mayank Jain
"""

from django.db import models
from django.contrib.auth.models import User, update_last_login, user_logged_in
user_logged_in.disconnect(update_last_login)

class AccountsToShow(models.Model):
    """Stores the accounts id's to be shown to the user according to user's preference"""
    username = models.CharField('Username', max_length=30)
    accountid = models.CharField('AccountId', max_length=10)

    def __unicode__(self):
        return u'%s' % (self.username)

class LoggedUsers(models.Model):
    """Stores the logged in clients and their Account_id"""
    username = models.CharField('Username', max_length=30, primary_key=True)
    account_id = models.IntegerField()

    def __unicode__(self):
        return u'%s, %s' % (self.username, self.account_id)

class Logs(models.Model):
    """Stores the logs of users login and logout"""
    STATUS_CHOICES = (
        ('Login', 'Login'),
        ('Logout', 'Logout'),
    )
    ATTEMPT_CHOICES = (
        ('S', 'SuccessFul'),
        ('F', 'Failed'),
    )
    status = models.CharField('Status', max_length=6, choices=STATUS_CHOICES, default='Login')
    username = models.CharField('Username', max_length=30)
    ip_address = models.GenericIPAddressField('IP Address')
    session_id = models.CharField('Session ID', max_length=100, blank=True)
    attempt = models.CharField('Attempt', max_length=1, choices=ATTEMPT_CHOICES, default='F')
    updated_at = models.DateTimeField('DateTime', auto_now_add=True)

    def __unicode__(self):
        return u'%s; %s; %s; %s; %s; %s' % (self.status, self.username, self.ip_address, self.session_id, self.attempt, self.updated_at)


class Listeners(models.Model):
    """Stores the connected listeners of push Notifications"""
    username = models.CharField('Username', max_length=30, primary_key=True)

    def __unicode__(self):
        return u'%s' % (self.username)
