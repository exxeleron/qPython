Managing connection
===================

qPython wraps connection to a q process in instances of the 
:class:`.QConnection` class.
::

  q = qconnection.QConnection(host = 'localhost', port = 5000, username = 'tu', password = 'secr3t', timeout = 3.0)
  try:
      q.open()
      # ...
  finally:
      q.close()

.. note:: the connection is not established when the connector instance is 
          created. The connection is initialized explicitly by calling the 
          :meth:`~qpython.qconnection.QConnection.open` method.


In order to terminate the remote connection, one has to invoke the 
:meth:`~qpython.qconnection.QConnection.close` method.

         
The :class:`.qconnection.QConnection` class provides a context manager API and 
can be used with a ``with`` statement:
::

  with qconnection.QConnection(host = 'localhost', port = 5000) as q:
      print q
      print q('{`int$ til x}', 10)


