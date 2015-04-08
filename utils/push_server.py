import zmq
import time
import message_pb2, config
#from message_pb2 import MessageType

# ZeroMQ Context
context = zmq.Context()

# Define the socket using the "Context"
push = context.socket(zmq.PUSH)
push.bind("tcp://%s:%s"%(config.API_HOST, config.API_PORT_TORNADO))

msg = message_pb2.WebMessages()

print "Server Started and listening at %s:%s"%(config.API_HOST, config.API_PORT_TORNADO)
# Run a simple "Echo" server
count = 0
while True:
    msg = message_pb2.WebMessages()
    if count == 0:
        msg.type = message_pb2.UPDATE_ACCOUNT
        msg.username = 'mjain'
        msg.updateaccount.accountdata.accountid = 35
        msg.updateaccount.accountdata.accountname = 'UT1'
        push.send(msg.SerializeToString())
        msg = message_pb2.WebMessages()
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 35
        msg.updaterisk.riskdata.netLiquidity = -1000000
        msg.updaterisk.riskdata.netProfitLoss = -500
        msg.updaterisk.riskdata.netMargin = 9000
        msg.updaterisk.riskdata.netBalance = -1000500
        msg.updaterisk.riskdata.netEquity = -991500
        count = 1
        time.sleep(0.01)
    elif count == 1:
        msg.type = message_pb2.UPDATE_ACCOUNT
        msg.username = 'mjain'
        msg.updateaccount.accountdata.accountid = 36
        msg.updateaccount.accountdata.accountname = 'UT2'
        push.send(msg.SerializeToString())
        msg = message_pb2.WebMessages()
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 36
        msg.updaterisk.riskdata.netLiquidity = 2000000
        msg.updaterisk.riskdata.netProfitLoss = 700
        msg.updaterisk.riskdata.netMargin = 4000
        msg.updaterisk.riskdata.netBalance = 3000500
        msg.updaterisk.riskdata.netEquity = 591500
        count = 2
        time.sleep(0.01)
    elif count == 2:
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 36
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = 7800500
        msg.updaterisk.riskdata.netEquity = 901500
        count = 3
        time.sleep(0.01)
    elif count == 3:
        msg.type = message_pb2.UPDATE_ACCOUNT
        msg.username = 'mjain'
        msg.updateaccount.accountdata.accountid = 37
        msg.updateaccount.accountdata.accountname = 'UT3'
        push.send(msg.SerializeToString())
        msg = message_pb2.WebMessages()
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 37
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = 7880500
        msg.updaterisk.riskdata.netEquity = 901500
        count = 4
        time.sleep(0.01)
    elif count == 4:
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 37
        msg.updaterisk.riskdata.netLiquidity = -5000000
        msg.updaterisk.riskdata.netProfitLoss = -800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = -7800500
        msg.updaterisk.riskdata.netEquity = -901500
        count = 5
        time.sleep(0.01)
    elif count == 5:
        msg.type = message_pb2.UPDATE_ACCOUNT
        msg.username = 'mjain'
        msg.updateaccount.accountdata.accountid = 38
        msg.updateaccount.accountdata.accountname = 'UT4'
        push.send(msg.SerializeToString())
        msg = message_pb2.WebMessages()
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 38
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 800
        msg.updaterisk.riskdata.netMargin = 60009
        msg.updaterisk.riskdata.netBalance = 7800500
        msg.updaterisk.riskdata.netEquity = 901500
        count = 6
        time.sleep(0.01)
    elif count == 6:
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 38
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = 7800500
        msg.updaterisk.riskdata.netEquity = 901500
        count = 7
        time.sleep(0.01)
    elif count == 7:
        msg.type = message_pb2.UPDATE_ACCOUNT
        msg.username = 'mjain'
        msg.updateaccount.accountdata.accountid = 39
        msg.updateaccount.accountdata.accountname = 'UT5'
        push.send(msg.SerializeToString())
        msg = message_pb2.WebMessages()
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 39
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = 7800500
        msg.updaterisk.riskdata.netEquity = 901500
        count = 8
        time.sleep(0.01)
    elif count == 8:
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 39
        msg.updaterisk.riskdata.netLiquidity = -5860000
        msg.updaterisk.riskdata.netProfitLoss = -800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = -7800500
        msg.updaterisk.riskdata.netEquity = -901500
        count = 9
        time.sleep(0.01)
    elif count == 9:
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 39
        msg.updaterisk.riskdata.netLiquidity = -5000000
        msg.updaterisk.riskdata.netProfitLoss = -800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = -7800580
        msg.updaterisk.riskdata.netEquity = -901500
        count = 10
        time.sleep(0.01)
    elif count == 10:
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 39
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = 7800580
        msg.updaterisk.riskdata.netEquity = 901500
        count = 11
        time.sleep(0.01)
    elif count == 11:
        msg.type = message_pb2.UPDATE_ACCOUNT
        msg.username = 'mjain'
        msg.updateaccount.accountdata.accountid = 34
        msg.updateaccount.accountdata.accountname = 'UT6'
        push.send(msg.SerializeToString())
        msg = message_pb2.WebMessages()
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 34
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 890
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = 7800500
        msg.updaterisk.riskdata.netEquity = 901500
        count = 12
        time.sleep(0.01)
    elif count == 12:
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 34
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = 7800500
        msg.updaterisk.riskdata.netEquity = 981500
        count = 13
        time.sleep(0.01)
    elif count == 13:
        msg.type = message_pb2.UPDATE_ACCOUNT
        msg.username = 'mjain'
        msg.updateaccount.accountdata.accountid = 33
        msg.updateaccount.accountdata.accountname = 'UT7'
        push.send(msg.SerializeToString())
        msg = message_pb2.WebMessages()
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 33
        msg.updaterisk.riskdata.netLiquidity = 5000000
        msg.updaterisk.riskdata.netProfitLoss = 800
        msg.updaterisk.riskdata.netMargin = 6000
        msg.updaterisk.riskdata.netBalance = 7800574
        msg.updaterisk.riskdata.netEquity = 901500
        count = 14
        time.sleep(0.01)
    else:
        msg.type = message_pb2.UPDATE_RISK
        msg.username = 'mjain'
        msg.updaterisk.accountid = 35
        msg.updaterisk.riskdata.netLiquidity = 2000089
        msg.updaterisk.riskdata.netProfitLoss = 678
        msg.updaterisk.riskdata.netMargin = 4567
        msg.updaterisk.riskdata.netBalance = 9870500
        msg.updaterisk.riskdata.netEquity = 986978
        count = 0
        time.sleep(0.01)
    push.send(msg.SerializeToString())
    print msg
    time.sleep(10)
