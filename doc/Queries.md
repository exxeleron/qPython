### Interacting with q

The `qPython` library supports both synchronous and asynchronous queries.

Synchronous query waits for service response and blocks requesting process until it receives the response. 

Asynchronous query does not block the requesting process and returns immediately without any result. The actual query result can be obtained either by issuing a corresponding request later on, or by setting up a listener to await and react accordingly to received data.

The `qPython` library provides following API methods in the `QConnection` class to interact with q: 

```python
# Executes a synchronous query against the remote q service.
def sync(self, query, *parameters)
def __call__(self, query, *parameters)

# Executes an asynchronous query against the remote q service.
def async(self, query, *parameters)

# Executes a query against the remote q service.
def query(self, msg_type, query, *parameters)
```

where:
* `query` is the definition of the query to be executed,
* `parameters` is a list of additional parameters used when executing given query,
* `msg_type` indicates type of the q message to be sent.

In typical use case, `query` is the name of the function to call and parameters are its parameters. When parameters list is empty the query can be an arbitrary q expression (e.g. `0 +/ til 100`).

In order to retrieve query result (for the `async()` or `query()` methods), one has to call:
```python
# Reads next message from the remote q service.
def receive(self, data_only = True, raw = False)
```

If the `data_only` parameter is set to `True`, only data part of the message is returned. If set to `False`, both data and message meta-information is returned as a wrapped as instance of `QMessage` class.

If the `raw` parameter is set to `False`, message is parsed and transformed to Python representation. If set to `True`, message is not parsed and raw array of bytes is returned.
