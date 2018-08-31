.. _connection:

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
          created. The connection is initialised explicitly by calling the 
          :meth:`~qpython.qconnection.QConnection.open` method.


In order to terminate the remote connection, one has to invoke the 
:meth:`~qpython.qconnection.QConnection.close` method.

         
The :class:`.qconnection.QConnection` class provides a context manager API and 
can be used with a ``with`` statement:
::

  with qconnection.QConnection(host = 'localhost', port = 5000) as q:
      print(q)
      print(q('{`int$ til x}', 10))


Types conversion configuration
******************************

Connection can be preconfigured to parse IPC messages according to a specified
settings, e.g.: temporal vectors can be represented as raw vectors or converted
to numpy `datetime64`/`timedelta64` representation.
::

  # temporal values parsed to QTemporal and QTemporalList classes
  q = qconnection.QConnection(host = 'localhost', port = 5000, numpy_temporals = False)
  
  # temporal values parsed to numpy datetime64/timedelta64 arrays and atoms
  q = qconnection.QConnection(host = 'localhost', port = 5000, numpy_temporals = True) 


Conversion options can be also overwritten while executing 
synchronous/asynchronous queries (:meth:`~qpython.qconnection.QConnection.sync`,
:meth:`~qpython.qconnection.QConnection.send`) or retrieving data from q
(:meth:`~qpython.qconnection.QConnection.receive`).



.. _custom_ipc_mapping:

Custom IPC protocol serializers/deserializers
*********************************************

Default IPC serializers (:class:`.QWriter` and :class:`._pandas.PandasQWriter`) and 
deserializers (:class:`.QReader` and :class:`._pandas.PandasQReader`) can be replaced 
with custom implementations. This allow users to override the default mapping 
between the q types and Python representation. 
::

  q = qconnection.QConnection(host = 'localhost', port = 5000, writer_class = MyQWriter, reader_class = MyQReader)


Refer to :ref:`custom_type_mapping` for details.