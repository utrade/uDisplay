#uDisplay
####uDisplay is web module based on Django and Tornado to display realtime data on web.

#Getting Started

## Installing Dependencies
```bash
   pip install -r requirements.txt
```
## Setting Up
Copy **uDisplay.example_local_settings.py** to **uDisplay.local_settings.py**.
Change settings in **uDisplay.local_settings.py**.

Modify **utils.config.py** to attach uDisplay to other data servers or test it with mock servers

* utils.test_server.py for authentication
* utils.push_server.py to push realtime data to be published

## Running
```python
   python manage.py runserver 0.0.0.0:port
   python socket_server.py
```

* Runserver starts django server
* socket_server starts the websocket server to push realtime data to web

```python
   python utils/test_server.py
   python utils/push_server.py
```

+ test_server is for authentication

  - Use any username and password for this server to get authenticated.
  - If you want push data from push_server use **utrade** as username.

+ push_server publish mock data for **utrade** client.

# License

This project is under the [GNU AGPL](./LICENSE) license.
