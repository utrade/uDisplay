"""
Tornado setup for neon project.

tornado.py
Created by Mayank Jain
"""

import threading
import time
import socket
from datetime import datetime
import simplejson
import os
import sys
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import sockjs.tornado
import tornado.wsgi
from utils import config
from Queue import Queue
import logging
from ctypes import *
import signal
import psycopg2
import json
import zmq
from utils import message_pb2
from utils import protobuf_json 

from inspect import getmodule
from multiprocessing.dummy import Pool

ROOT = os.path.dirname(os.path.abspath(__file__))
#---------Logger --------------#
logger = logging.getLogger(__name__)
hdlr = logging.StreamHandler()
hdlr.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
#--------Logger--------------#
PORT = config.TornadoPort
Data_Cache = {} # Buffering Cache for sending data after 1 second
Data_Accounts_Cache = {} # Cache to store data till browser connects to socket


def _execute(query):
    """Function to execute queries against a local sqlite database
        :param query: SQL Query
    """
    conn = psycopg2.connect("dbname=%s user=%s password=%s port=%s"%(config.DBNAME, config.USER, config.PASSWORD, config.PORT))
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(query)
        try:
            result = cur.fetchall()
        except BaseException,e:
            result = None
        cur.close()
        conn.close()
    except Exception:
        raise
    return result

# Empty listeners from Database on tornado start
_execute("DELETE FROM risk_management_listeners;")

def zmq_socket(pool):
    """Function to start zmq socket
        :param pool: Thread pool for sending message to web
    """

    # ZeroMQ Context
    context = zmq.Context()

    # Define the socket using "Context"
    sock = context.socket(zmq.PULL)
    sock.connect("tcp://%s:%s"%(config.API_HOST, config.API_PORT_TORNADO))

    # Run a simple server
    flag = 'run'
    msg = message_pb2.WebMessages()
    logger.info("ZMQ Socket Started")
    while flag != 'stop':
        message = ''
        try:
            message = sock.recv() # Receiving Data from API
            msg.ParseFromString(message)
            data = protobuf_json.pb2json(msg)
        except BaseException,e:
            logger.error("Error in receiving data")
        if message != '':
            pool.apply_async(send_msg_to_web_console, (data,))


class API_SocketThread(threading.Thread):
    """ Class for assigning socket and queue values to class members
        Class for starting thread to recieve market data.
        :param Asocket: API Socket
        :param AQueue: API Data queue
    """
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.pool = Pool(processes=num_threads)
        threading.Thread.__init__(self)
    def run(self):
        zmq_socket(self.pool)

def send_msg_to_web_console(message):
    """ Method for sending push data to logged in clients in web.
        :param message: Push Data to be sent to Web Frontend.
    """
    clientid = message['username']

    global Data_Cache # To store push data which will be send after fix time
    global Data_Accounts_Cache # Store push data till client connects to browser which will be deleted on client disconnect
    
    try:
        Data = {}
        TotalsData = {}
        Data['username'] = clientid

        # Serialize update account data
        if message['type'] == message_pb2.LOGOUT_RESPONSE:
            try: 
                LoggedClients = {}
                rows = _execute('SELECT * FROM risk_management_loggedusers;')
                if rows != None:
                    for row in rows:
                        LoggedClients[row[0]] = row[1]
            except BaseException,e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                return
            try:
                if clientid in LoggedClients.keys():
                    request = Listeners[client]
                    request.send("Logout")
                else:
                    return
            except BaseException,e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                return

        if message['type'] == message_pb2.UPDATE_ACCOUNT:
            if message['updateaccount']['accountdata']:
                Data['accountid'] = message['updateaccount']['accountdata']['accountid']
                Data['accountname'] = message['updateaccount']['accountdata']['accountname']
            else:
                Data['error'] = 'Data not Available from Backend'

            if Data_Cache.get(clientid):
                account_ids = [dict.keys()[0] for dict in Data_Cache[clientid]]
                accounts_cache_ids = [dict.keys()[0] for dict in Data_Accounts_Cache[clientid]]
                if Data['accountid'] in account_ids:
                    Data_Cache[clientid][account_ids.index(Data['accountid'])][Data['accountid']]['accountdata'] = Data
                else:
                    Data_Cache[clientid].append({Data['accountid']:{'accountdata': Data}})
                if Data['accountid'] in accounts_cache_ids:
                    Data_Accounts_Cache[clientid][accounts_cache_ids.index(Data['accountid'])][Data['accountid']]['accountdata'] = Data
                else:
                    Data_Accounts_Cache[clientid].append({Data['accountid']:{'accountdata': Data}})
            else:
                Data_Cache[clientid] = []
                Data_Cache[clientid].append({Data['accountid']:{'accountdata': Data}})
                Data_Accounts_Cache[clientid] = []
                Data_Accounts_Cache[clientid].append({Data['accountid']:{'accountdata': Data}})

        # Serialize update risk data
        elif message['type'] == message_pb2.UPDATE_RISK:
            # Risk data
            if message['updaterisk'].get('riskdata'):
                Data['accountid'] = message['updaterisk']['accountid']
                Data['netLiquidity'] = message['updaterisk']['riskdata']['netLiquidity']
                Data['netProfitLoss'] = message['updaterisk']['riskdata']['netProfitLoss']
                Data['netMargin'] = message['updaterisk']['riskdata']['netMargin']
                Data['netBalance'] = message['updaterisk']['riskdata']['netBalance']
                Data['netEquity'] = message['updaterisk']['riskdata']['netEquity']
                if int(Data['netLiquidity']) != 0:
                    try:
                        Data['netProfitLossPer'] = '%.2f'%((float(Data['netProfitLoss'])/float(Data['netLiquidity']))*100)
                        Data['netMarginPer'] = '%.2f'%((float(Data['netMargin'])/float(Data['netLiquidity']))*100)
                    except BaseException,e:
                        logger.info(e);
                        Data['netProfitLossPer'] = '0.0'
                        Data['netMarginPer'] = '0.0'
                else:
                    Data['netProfitLossPer'] = '0.0'
                    Data['netMarginPer'] = '0.0'
            else:
                Data['error'] = 'Data not Available from Backend'

            if Data_Cache.get(clientid):
                account_ids = [dict.keys()[0] for dict in Data_Cache[clientid]]
                accounts_cache_ids = [dict.keys()[0] for dict in Data_Accounts_Cache[clientid]]
                if Data['accountid'] in account_ids:
                    Data_Cache[clientid][account_ids.index(Data['accountid'])][Data['accountid']]['riskdata'] = Data
                else:
                    Data_Cache[clientid].append({Data['accountid']:{'riskdata': Data}})
                if Data['accountid'] in accounts_cache_ids:
                    Data_Accounts_Cache[clientid][accounts_cache_ids.index(Data['accountid'])][Data['accountid']]['riskdata'] = Data
                else:
                    Data_Accounts_Cache[clientid].append({Data['accountid']:{'riskdata': Data}})
            else:
                Data_Cache[clientid] = []
                Data_Cache[clientid].append({Data['accountid']:{'riskdata': Data}})
                Data_Accounts_Cache[clientid] = []
                Data_Accounts_Cache[clientid].append({Data['accountid']:{'riskdata': Data}})

        else:
            Data['error'] = 'Data not Available from Backend'
            TotalsData['error'] = 'Data not Available from Backend'

    except BaseException,e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print "Error is", e
        logger.error("Error in Sending Message Data : %s"%str(e))
        #special encoding for rejection message in data
        try:
            list_ = list(['Accounts'])
            list_[5] = unicode(list_[5], 'ISO-8859-1')
            Data = tuple(list_)
            logger.info(request.send(unicode(simplejson.dumps(Data))))
        except Exception, ex:
            logger.error("Error in sending Message Data : %s"%str(ex))

def Timer():
    """Function to send updated data to clients after fix time from cache.
       This function is used to send more frequent updates after fix time instead of real time.
    """
    global Data_Cache

    try: 
        LoggedClients = {}
        rows = _execute('SELECT * FROM risk_management_loggedusers;')
        if rows != None:
            for row in rows:
                LoggedClients[row[0]] = row[1]
    except BaseException,e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        # Add another timeout of fix time
        WebData.add_timeOut()
        return

    for client in Listeners.keys():
        try:
            if client in LoggedClients.keys():
                if Data_Cache.get(client):
                    request = Listeners[client]
                    for data in Data_Cache[client]:
                        key = data.keys()[0]
                        if data[key].get('accountdata'):
                            request.send(data[key]['accountdata'])
                            print("Sending %s Data:- %s"%(client, data[key]['accountdata']))
                            del data[key]['accountdata']
                        if data[key].get('riskdata'):
                            request.send(data[key]['riskdata'])
                            print("Sending %s Data:- %s"%(client, data[key]['riskdata']))
                            del data[key]['riskdata']
        except BaseException,e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    # Add another timeout of 1 second
    WebData.add_timeOut()



class EchoWebSocket(sockjs.tornado.SockJSConnection):
    """
    Class Inheriting sockjs.tornado.SockJSConnection to establish the Socket Connection Request
    
    from sockjs connection object
    """
    def on_open(self,info):
        """ Method to Open the Socket Connection"""
        self.send(unicode('add'))
        logger.info("Connection Opened")

    def on_message(self, message):
        """Method to Read the Socket Connection Message"""

        global Clients # Django logged in clients
        global db_listeners # websocket connected clients
        global Data_Accounts_Cache
        Clients = {}
        db_listeners = []

        parameters = message.decode('utf-8').split(';')
        task = parameters[0]
        client = str(parameters[1]) # username
        if task == 'add':
            # get the django logged in clients from db
            rows = _execute('SELECT * FROM risk_management_loggedusers;')
            if rows != None:
                for row in rows:
                    Clients[row[0]] = row[1]

            # get the websocket connected clients from db
            rows = _execute('SELECT * From risk_management_listeners;')
            print rows
            if rows != None:
                for row in rows:
                    db_listeners.append(row[0])
            print 'db_listeners', db_listeners
            
            # if new client already exist in websocket connected clients
            if client in db_listeners:
                self.send(unicode(simplejson.dumps({'Error': 'Privacy error, User already logged in!'})))
                try:
                    Listeners[client].send(unicode(simplejson.dumps({'Error' : 'Somebody tries to login to your account. If its not you then change your password immediatly'})))
                except BaseException,e:
                    print e
                return

            # Checking the client logged in django or not
            if len(Clients.keys()) > 0:
                if client in Clients.keys():
                    # Adding client to db
                    _execute("""INSERT INTO risk_management_listeners (username) VALUES ('%s');"""%(client))
                    rows = _execute('SELECT * From risk_management_listeners;')
                    print rows

                    # saving client socket in Listeners dict
                    Listeners.update({client:self})

                    if Data_Accounts_Cache.get(client):
                        for data in Data_Accounts_Cache[client]:
                            key = data.keys()[0]
                            if data[key].get('accountdata'):
                                self.send(data[key]['accountdata'])
                            if data[key].get('riskdata'):
                                self.send(data[key]['riskdata'])
            else:
                return
        elif task == 'del':
            try:
                # Removing user from websocket connected list
                _execute("DELETE FROM risk_management_listeners WHERE username = '%s';"%(client))

                # Removing user from websocket connected dict
                del(Listeners[usr])
            except BaseException,e:
                logger.info("Exception in removing%s"%str(e))

    def on_close(self):
        """Method to Close the Socket Connection and remove the client from Listeners"""
        try:
            # Gets a list of sockets from Listeners dict
            sockets = Listeners.values()

            # Gets the user by finding the index in sockets list
            usr = Listeners.keys()[sockets.index(self)] 

            # Removing user from websocket connected list
            _execute("DELETE FROM risk_management_listeners WHERE username = '%s';"%(usr))
            rows = _execute('SELECT * From risk_management_listeners;')
            print rows

            # Removing user from websocket connected dict
            del(Listeners[usr])
            logger.info("Connection Closed to client "+usr)

            while len(Data_Accounts_Cache[usr]):
                Data_Accounts_Cache[usr].pop()

        except BaseException, e:
            logger.info("Connection Closed"+e)

ChatRouter = sockjs.tornado.SockJSRouter(EchoWebSocket,'/socket')
application = tornado.web.Application(
    ChatRouter.urls,
)

Listeners = {}  # Dict containing mapping of Client with its Request Object e.g. {'CLIENT1': RequestObject, ..}
Clients = {} # Dict containing Django logged in clients
db_listeners = [] # List containing websocket connected listeners

logger.info("Starting Web Socket Server")

class DataProcessing(object):
  """ Class to Access the functionality of Socket Data and Other Notifications """
  def __init__(self,Clients,Listeners,application):
    self.Clients = Clients  # Client List (Currently Logged In)
    self.Listeners = Listeners	 # Listeners Dict containing Request Objects for each Client in Client List
    self.ServerStatus = False
    self.application = application  # Tornado Server Application Object
    self.AQueue = Queue()   # Queue common for API Socket and Data Processing thread
    self.ASocket = API_SocketThread(5) # Passing number of threads as argument
    self.ASocket.start()

  def add_timeOut(self):
      """ Method for adding timer to tornado loop """
      try:
          self.io_loop.add_timeout(time.time() + 1, lambda:Timer())
      except BaseException,e:
          logger.error(str(e))

  def start_tornado_server(self):
    """ Method for Starting Tornado Server """
    try:
      logger.info("Starting Tornadio2 Server")
      self.application.listen(PORT)
      self.ServerStatus = True
      self.io_loop = tornado.ioloop.IOLoop.instance()
      Timer()
      self.io_loop.start()
    except BaseException,e:
      logger.error(str(e))

  def stop_tornado_server(self):
    """ Method for Stoping Tornado Server """
    logger.info("Stopping Tornadio2 Server")
    self.io_loop.stop()
    logger.info("Stopped Tornadio2 Server")

  def signal_handler(self,signal,frame):
    """ Method for Handling Signal Request """
    if self.ServerStatus:
      self.stop_tornado_server()

try:
    WebData = DataProcessing(Clients, Listeners, application)
    WebData.start_tornado_server()                 # Staring Tornado Server.
except BaseException,e:
    logger.info("Error in starting Web Socket Server")
    logger.error(str(e))
#signal.signal(signal.SIGINT,WebData.signal_handler)
#signal.pause()
logger.info("Web Socket Server Stopped")
