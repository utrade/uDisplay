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

    uDisplay is web module based on Django and Tornado to display realtime data on web.
    Copyright (C) 2015 uTrade Solutions Pvt. Ltd.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Contributions

Pull Requests and Bug reports are welcome via Github.
