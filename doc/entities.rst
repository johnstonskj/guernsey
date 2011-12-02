Guernsey Entity Reader/Writer Module
------------------------------------

.. automodule:: guernsey.entities

This module provides a pair of classes used to support marshalling and
unmarshalling data to/from Python. The ``EntityReader`` class allows
the automatic unmarshalling from an encoded form in the response from 
a service into Python.  The ``EntityWriter`` class allows the 
automatic marshalling of a Python object in a request into the
appropriate encoded form.  Both of these classes use the 
``Content-Type`` header to denote the encoded form.

The following example shows how these are typically used in the client,
the client has a set of default configured entity classes (which can be 
added to or reduced as needed) which are scanned for any request and
response. If a matching entity class is found for the request or
response it is used to convert to/from Python. In this case we see that
the ``entity`` property on the response has been parsed into the 
``parsed_entity`` property; the original value is retained as a string
but the JSON has been parsed into a standard Python dictionary.::

  import guernsey
  c = guernsey.Client.create()
  print c.entity_classes
  [<JsonReader object>, <JsonWriter object>, <XmlReader object>, <XmlWriter object>]
  ...
  response = resource.get()
  print repr(response.entity)
  '{"name": "test"}'
  print response.parsed_entity
  {u'name': u'test'}

Base Classes
************

.. autoclass:: guernsey.entities.EntityReader
   :members:

.. autoclass:: guernsey.entities.EntityWriter
   :members:

Standard Reader/Writer Classes
******************************

.. autoclass:: guernsey.entities.JsonReader

.. autoclass:: guernsey.entities.JsonWriter

.. autoclass:: guernsey.entities.XmlReader

.. autoclass:: guernsey.entities.XmlWriter
