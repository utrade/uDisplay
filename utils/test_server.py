import zmq
import message_pb2
import config

# ZeroMQ Context
context = zmq.Context()

# Define the socket using the "Context"
sock = context.socket(zmq.REP)
sock.bind("tcp://%s:%s"%(config.API_HOST, config.API_PORT_DJANGO))
#push = context.socket(zmq.PUSH)
#push.connect("tcp://127.0.0.1:27015")

msg = message_pb2.WebMessages()
reply = message_pb2.WebMessages()
#types = message_pb2.MessageType()
#`print types.LOGIN_REQUEST

print "Server Started and listening at %s:%s"%(config.API_HOST, config.API_PORT_DJANGO)
# Run a simple "Echo" server
while True:
    try:
        message = ''
        message = sock.recv()
    except BaseException,e:
        logger.error("Error in recieving data")
    msg.ParseFromString(message)
    if msg.type == 1:
        reply.type = 2
        reply.username = msg.username
        reply.loginresponse.isLogged = True
    elif msg.type == 3:
        reply.type = 4
        reply.username = msg.username
        reply.logoutresponse.isLogged = True
    elif msg.type == 5:
        reply.type = 6
        reply.username = msg.username
    elif msg.type == 7:
        reply.type = 8
        reply.username = msg.username
    else:
        reply.type = 11
        reply.username = msg.username
    sock.send(reply.SerializeToString())
    print "Echo: ", msg
