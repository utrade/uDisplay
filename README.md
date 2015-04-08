#uDisplay
#####uDisplay is web module based on Django and Tornado to display realtime data on web.

#Getting Started

## Installing Dependencies
```pip install -r requirements.txt```

## Setting Up
###### Copy uDisplay.example_local_settings.py to uDisplay.local_settings.py
###### Change settings in uDisplay.local_settings.py

Modify utils.config.py to attach uDisplay to other data servers or test it with mock servers
* utils.test_server.py for authentication
* utils.push_server.py to push realtime data to be published

## Running
```python manage.py runserver 0.0.0.0:port```
```python socket_server.py```
#####Runserver starts django server
#####socket_server starts the websocket server to push realtime data to web

```python utils/test_server.py```
```python utils/push_server.py```
#####test_server is for authentication
>Use any username and password for this server to get authenticated. But if you want push data from push_server use 'mjain' as username.
#####push_server publish mock data for 'mjain' client.
