"""
Views for risk_management app.

risk_management/views.py
Created by Mayank Jain
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import RequestContext
from .models import LoggedUsers, AccountsToShow

import zmq, json, pickle
from utils import message_pb2, config
from utils import protobuf_json 

@login_required(login_url='/login')
def accounts(request):
    """Returns the initial data of accounts page from API"""

    usr = request.user

    # Send accounts data request of user to API
    # ZeroMQ Context
    context = zmq.Context()

    # Define the socket using the "Context"
    sock = context.socket(zmq.REQ)
    sock.connect("tcp://%s:%s"%(config.API_HOST, config.API_PORT_DJANGO))

    # Send a user accounts request using the socket
    message = message_pb2.WebMessages()
    message.type = message_pb2.ACCOUNT_REQUEST
    message.username = str(usr)
    sock.send(message.SerializeToString())
    
    sock.linger = 0
    poller = zmq.Poller()
    poller.register(sock, zmq.POLLIN)
    conn = dict(poller.poll(10000))
    if conn:
        if conn.get(sock) == zmq.POLLIN:
            data = sock.recv(zmq.NOBLOCK)

            #data = sock.recv()
            message = message_pb2.WebMessages()
            message.ParseFromString(data)
            print "Accounts Data :- ", message
            data = protobuf_json.pb2json(message)
            if message.type == message_pb2.ERROR_MESSAGE:
                if data.get('errortype'):
                    if message.errortype == message_pb2.ACCOUNT_REQUESTED_AT_LOGOFF:
                        messages.set_level(request, messages.WARNING)
                        messages.warning(request, 'Your session expired. Please login again.')
                        return HttpResponseRedirect('/login')
                data = None
    else:
        print('Got no result')
        data = None

    # Get the Selected Accounts List
    try:
        selected_accounts_list = [int(account.accountid) for account in AccountsToShow.objects.filter(username=request.user.username)]
    except:
        selected_accounts_list = []

    result = {}
    result['username'] = request.user.username   # Modify according to frontend
    result['TornadoPort'] = config.TornadoPort
    result['SocketPath'] = config.SocketPath
    result['selected_accounts_list'] = selected_accounts_list
    if data:
        if data['type'] == message_pb2.ACCOUNT_DETAILS:
            if data['username'] == request.user.username:
                result['data'] = data
                if result['data'].get('accountdetails'):
                   for account in result['data']['accountdetails']:
                       if account.get('riskdata') and int(account['riskdata']['netLiquidity'])!=0:
                           try:
                               account['riskdata']['netProfitLossPer'] = '%.2f'%((float(account['riskdata']['netProfitLoss'])/float(account['riskdata']['netLiquidity']))*100)
                               account['riskdata']['netMarginPer'] = '%.2f'%((float(account['riskdata']['netMargin'])/float(account['riskdata']['netLiquidity']))*100)
                               if account['riskdata']['netProfitLossPer'] == '-0.00':
                                   account['riskdata']['netProfitLossPer'] = '0.00'
                               if account['riskdata']['netMarginPer'] == '-0.00':
                                   account['riskdata']['netMarginPer'] = '0.00'
                           except BaseException,e:
                               print(e)
                               account['riskdata']['netProfitLossPer'] = '0.0'
                               account['riskdata']['netMarginPer'] = '0.0'
                       else:
                           account['riskdata']['netProfitLossPer'] = '0.0'
                           account['riskdata']['netMarginPer'] = '0.0'

                else:
                    result['error'] = 'Does not get Data from API'
            else:
                result['error'] = 'Does not get Data from API'
        else:
            result['error'] = 'Does not get Data from API'
    else:
        result['error'] = 'Does not get Data from API'
    return render_to_response('risk_management/accounts.html', {'result': result},context_instance=RequestContext(request))


@login_required(login_url='/login')
def save_account_ids(request):
    accounts_list = request.GET.getlist('accounts')
    user = str(request.user)
    user_accounts = AccountsToShow.objects.filter(username=user)
    user_accountsIds = [account.accountid for account in user_accounts]
    for account in accounts_list:
        if account not in user_accountsIds:
            AccountsToShow.objects.create(username=user, accountid=account)
    for account in user_accounts:
        if account.accountid not in accounts_list:
            account.delete()
    return HttpResponse(json.dumps('Accounts Saved'), content_type="application/json")
