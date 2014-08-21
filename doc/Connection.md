### Connection object

Connection to the q process can be done by using instance of the `QConnection` class. The `QConnection` class provides following `__init__` method:

```python
class QConnection:
  def __init__(self, host, port, username = None, password = None, timeout = None)
```

where:
- `host` - q hostname
- `port` - q port
- `username` (optional) - username for q authentication/authorization
- `password` (optional) - password for q authentication/authorization
- `timeout` (optional) - socket timeout


### Managing the remote connection

Note that the connection is not established when the connector instance is created. The connection is initialized explicitly by calling the `open()` method.

In order to terminate the remote connection, one has to invoke the `close()` method.

The `is_connected()` method checks if connection has been initialized.