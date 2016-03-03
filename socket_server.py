"""
Tornado socket server setup

tornado.py
Created by Mayank Jain
"""

import logging
import os
import signal
import threading
from multiprocessing.dummy import Pool

import django
import environ
import simplejson
import sockjs.tornado
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.wsgi
import zmq
from dotenv import load_dotenv
from udisplay.base.utils import message_pb2, protobuf_json

# Setting up dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
env = environ.Env()

# setup django
os.environ['DJANGO_SETTINGS_MODULE'] = env.str("DJANGO_SETTINGS_MODULE", "settings.development")
PORT = env.int('TornadoPort', 9988)
django.setup()

from udisplay.users.services import get_user_for_token  # NOQA

# ---------Logger -------------- #
logger = logging.getLogger(__name__)
hdlr = logging.StreamHandler()
hdlr.setFormatter(logging.Formatter('%(asctime)s - '
                                    '%(name)s - %(levelname)s - %(message)s'))
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
# --------Logger-------------- #


def zmq_socket(pool, exit_app):
    """Function to start zmq socket
        :param pool: Thread pool for sending message to web
        :param exit_app: Exit app flag to stop the thread
    """

    # ZeroMQ Context
    context = zmq.Context()

    # Define the socket using "Context"
    sock = context.socket(zmq.PULL)
    sock.connect("tcp://{}:{}".format(env.str('API_HOST', '127.0.0.1'),
                                      env.int('API_PORT_TORNADO', 26016)))

    # Run a simple server
    msg = message_pb2.WebMessages()
    logger.info("ZMQ Socket Started")
    while not exit_app:
        message = None
        try:
            message = sock.recv()  # Receiving Data from API
            msg.ParseFromString(message)
            data = protobuf_json.pb2json(msg)
        except (zmq.ZMQError, zmq.ZMQVersionError,
                zmq.Again, zmq.ContextTerminated,
                zmq.NotDone, zmq.ZMQBindError) as e:
            logger.error("Error in receiving data: {}".format(e))
        if message:
            pool.apply_async(send_msg_to_web_console, (data,))


class API_SocketThread(threading.Thread):
    """ Class for assigning socket and queue values to class members
        Class for starting thread to recieve market data.
        :param num_threads: Number of threads for thread pool
    """
    def __init__(self, num_threads, exit_app):
        self.num_threads = num_threads
        self.pool = Pool(processes=num_threads)
        self.exit_app = exit_app
        threading.Thread.__init__(self)

    def run(self):
        zmq_socket(self.pool, self.exit_app)


def send_msg_to_web_console(message):
    """ Method for sending push data to logged in clients in web.
        :param message: Push Data to be sent to Web Frontend.
    """
    for client in Listeners.keys():
        try:
            request = Listeners[client]
            logger.info("msg: {}".format(str(message)))
            if message.get('updaterisk'):
                request.send(message.get('updaterisk').get('riskdata'))
            if message.get('updateaccount'):
                request.send(message.get('updateaccount').get('accountdata'))
        except BaseException as e:
            logger.error("Error in sending data to user {}: {}".format(client, e))


class EchoWebSocket(sockjs.tornado.SockJSConnection):
    """
    Class Inheriting sockjs.tornado.SockJSConnection
    establish the Socket Connection Request

    from sockjs connection object
    """
    def on_open(self, info):
        """ Method to Open the Socket Connection"""
        self.send('add')
        logger.info("Connection Opened")

    def on_message(self, message):
        """Method to Read the Socket Connection Message"""

        parameters = message.split(';')
        task = parameters[0]
        client = str(parameters[1])  # username
        if task == 'add':
            token = str(parameters[2])
            user = get_user_for_token(token, 'auth')

            # if new client already exist in websocket connected clients
            if client in Listeners.keys():
                self.send(simplejson.dumps({'Error': 'Privacy error,'
                                                     'User already '
                                                     'logged in!'}))
                try:
                    error_msg = {'Error': 'Somebody tries to login to your '
                                          'account. If its not you then '
                                          'change your password immediatly'}
                    Listeners[client].send(simplejson.dumps(error_msg))
                except BaseException as e:
                    logger.info("Error: {}".format(e))

                return

            # saving client socket in Listeners dict
            Listeners.update({user: self})

        elif task == 'del':
            # Removing user from websocket connected dict
            user = Listeners.keys()[Listeners.values().index(self)]
            del(Listeners[user])
            logger.info("Connection removed to client {}".format(user))

    def on_close(self):
        """Method to Close the Socket Connection
           remove the client from Listeners
        """
        # Removing user from websocket connected dict
        user = Listeners.keys()[Listeners.values().index(self)]
        del(Listeners[user])
        logger.info("Connection Closed to client {}".format(user))

ChatRouter = sockjs.tornado.SockJSRouter(EchoWebSocket, '/socket')
application = tornado.web.Application(
    ChatRouter.urls,
)

# Dict containing mapping of Client with its Request Object
# e.g. {'CLIENT1': RequestObject, ..}
Listeners = dict()

logger.info("Starting Web Socket Server")


class DataProcessing(object):
    """
    Class to Access the functionality of Socket Data and Other Notifications
    """
    def __init__(self, Listeners, application):
        # Listeners Dict containing Request Objects for each Client
        self.Listeners = Listeners

        # Tornado Server Application Object
        self.application = application

        # Socket thread stop flag
        self.exit_app = False

        # Passing number of threads as argument
        self.ASocket = API_SocketThread(5, self.exit_app)
        self.ASocket.start()

    def start_tornado_server(self):
        """ Method for Starting Tornado Server """
        logger.info("Starting Tornadio2 Server")
        self.application.listen(PORT)
        self.io_loop = tornado.ioloop.IOLoop.instance().start()

    def stop_tornado_server(self):
        """ Method for Stoping Tornado Server """
        logger.info("Stopping Tornadio2 Server")
        self.io_loop.stop()
        logger.info("Stopped Tornadio2 Server")

    def signal_handler(self, signal, frame):
        """ Method for Handling Signal Request """
        self.exit_app = True
        self.stop_tornado_server()

WebData = DataProcessing(Listeners, application)
WebData.start_tornado_server()  # Staring Tornado Server.
signal.signal(signal.SIGINT, WebData.signal_handler)
signal.pause()
logger.info("Web Socket Server Stopped")
