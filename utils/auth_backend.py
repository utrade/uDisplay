"""
Custom Authentication Backend to authenticate from other servers
utils/auth_backend.py

Created By Mayank Jain
"""
from django.contrib.auth.models import User
from django.contrib.auth.backends import RemoteUserBackend
from risk_management.models import LoggedUsers, Listeners
import time
import sys
import zmq
import message_pb2
import config
from utils import protobuf_json 

def get_client_ip(request):
    """Method for getting IP address from the request headers for Logs."""

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class Backend(object):
    """Class for Django Authentication to web frontend.

       It will modify the django-auth default backend by validating user from API instead of database.
    """

    def authenticate(self, username=None, password=None):
        """Method for validating whether user exist in API or not

        Keyword arguments:
        username -- username (default None)
        password -- password (default None)
        """

        # ZeroMQ Context
        context = zmq.Context()

        # Define the socket using the "Context"
        sock = context.socket(zmq.REQ)
        sock.connect("tcp://%s:%s"%(config.API_HOST, config.API_PORT_DJANGO))
        print "connected to", config.API_HOST, config.API_PORT_DJANGO

        # Send a user auth request using the socket and protobuf
        message = message_pb2.WebMessages()
        message.type = message_pb2.LOGIN_REQUEST
        message.username = username
        message.loginrequest.password = password
        sock.send(message.SerializeToString())
    
        sock.linger = 0
        poller = zmq.Poller()
        poller.register(sock, zmq.POLLIN)
        conn = dict(poller.poll(60000))
        if conn:
            if conn.get(sock) == zmq.POLLIN:
                msg = sock.recv(zmq.NOBLOCK)

                message = message_pb2.WebMessages()
                message.ParseFromString(msg)
                print "UserExist", message
                try:
                    if message.username == username:
                        if message.type == message_pb2.LOGIN_RESPONSE:
                            user_exist = message.loginresponse.isLogged
                        else:
                            data = protobuf_json.pb2json(message)
                            if data.get('errortype'):
                                print(message.errortype)
                            user_exist = False
                    else:
                        user_exist = False
                except:
                    print('Error', sys.exc_info())
                    user_exist = False
        else:
            print('Got no result')
            user_exist = False
            return None

        #user_exist = True # Attach with API
        print user_exist

        if not user_exist:
            return None
        else:
            try:
                # Create a user object for maintaing auth and sessions
                usr = User.objects.create_user(username=username, password=password)
            except:
                # User already logged in from some other location.
                # Delete user from User, LoggedUsers, Listeners and create new user.
                try:
                    old_user = User.objects.get(username=username)
                except:
                    return None

                try:
                    LoggedUsers.objects.get(username=username).delete()
                except:
                    pass

                try:
                    Listeners.objects.get(username=username).delete()
                except BaseException,e:
                    pass

                # Saving Logs
                try:
                    Logs.objects.create(status='Logout', username=username, ip_address=get_client_ip(request), session_id=old_user.get_session_auth_hash(), attempt='S')
                except:
                    print "Logs can't be saved", sys.exc_info()[0]

                old_user.delete()
                usr = User.objects.create_user(username=username, password=password)
            return usr

    def get_user(self, user_id):
        """Method for returning user object for giver user id
            :param user id: as user_id
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
