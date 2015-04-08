"""
uDisplay/views.py
Created by Mayank Jain
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from .forms import LoginForm
from risk_management.models import LoggedUsers, Logs, Listeners

from utils.auth_backend import get_client_ip
from utils import message_pb2
from utils import config

import sys
import zmq

def login_view(request):
    """Method to check validity of submit form and checks user authentication.
       If user is valid then redirect to accounts page.
       If method is not POST then returns a new instance of login form.
    """
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            # Uses custom backend for authentication
            print "Authenticating..."
            user = authenticate(username=username, password=password)
            msg = 0
            if (user is not None):
                if user.is_active:
                    login(request, user)
                    LoggedUsers.objects.create(username=username, account_id=1)

                    # Saving Logs
                    try:
                        Logs.objects.create(status='Login', username=username, ip_address=get_client_ip(request), session_id=user.get_session_auth_hash(), attempt='S')
                    except:
                        print "Logs can't be saved", sys.exc_info()[0]

                    # Redirect to a success page.
                    return HttpResponseRedirect('/')

                #else:
                    # Return a 'disabled account' error message.

            else:
                # Return an 'invalid login' error message.
                if user == False:
                    form.errors['Unable'] = ' to contact server. Please contact XXX if the problem persists.'
                else:
                    form.errors['Account'] = ' is disabled or username and password does not match.'
                # Saving Logs
                try:
                    Logs.objects.create(status='Login', username=username, ip_address=get_client_ip(request), attempt='F')
                except:
                    print("Logs can't be saved", sys.exc_info()[0])

    return render_to_response('login.html', {'form': form}, context_instance=RequestContext(request))

def logout_view(request):
    """Method to logout user from API, delete its session and user objects from database"""
    usr = request.user

    # Send logout request of user to API and delete user object from User and LoggedUsers
    # ZeroMQ Context
    context = zmq.Context()

    # Define the socket using the "Context"
    sock = context.socket(zmq.REQ)
    sock.connect("tcp://%s:%s"%(config.API_HOST, config.API_PORT_DJANGO))

    # Send a user auth request using the socket and protobuf
    message = message_pb2.WebMessages()
    message.type = message_pb2.LOGOUT_REQUEST
    message.username = str(usr)

    # Sending Request for Data
    sock.linger = 0
    sock.send(message.SerializeToString())
    
    poller = zmq.Poller()
    poller.register(sock, zmq.POLLIN)
    conn = dict(poller.poll(1000))
    if conn:
        if conn.get(sock) == zmq.POLLIN:
            user_logged_out = sock.recv(zmq.NOBLOCK)
            #user_logged_out = sock.recv()

    else:
        print('Got no result')
    user_logged_out = False


    logout(request)

    # Removing from LoggedUsers if exist
    try:
        LoggedUsers.objects.get(username=usr).delete()
    except BaseException,e:
        print(e)

    # Removing from Listeners if exist
    try:
        Listeners.objects.get(username=usr).delete()
    except BaseException,e:
        print(e)

    # Saving Logs
    try:
        Logs.objects.create(status='Logout', username=usr, ip_address=get_client_ip(request), session_id=usr.get_session_auth_hash(), attempt='S')
    except:
        print("Logs can't be saved", sys.exc_info()[0])

    try:
        User.objects.get(username=usr).delete()
    except:
        print(sys.exc_info())

    # Redirect to login page
    return HttpResponseRedirect('/')
