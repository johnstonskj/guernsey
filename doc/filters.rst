Guernsey Request/Response Filter Module
---------------------------------------

.. automodule:: guernsey.filters

This module provides a set of useful filters that can be applied
to resources to add additional HTTP behavior to clients. Where 
possible any behavior not core to the HTTP protocol will be 
factored into one or more filters rather than add to either the
:class:`Client` or :class:`WebResource` classes.

Standard Filters
****************

The following deal with very common use cases and may be expected
to be used in many cases.

.. autoclass:: guernsey.filters.LoggingFilter
   :members:

*LoggingFilter Example*

The following example demonstrates the basic addition of the 
:class:`LoggingFilter` to the filter chain for a resource.::

  import logging

  FORMAT = '%(asctime)-15s %(levelname)s %(thread)d %(message)s'
  logging.basicConfig(format=FORMAT, level=logging.DEBUG)

  client = Client.create()
  namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/')
  namespaces.add_filter(LoggingFilter('TestFilterLogging'))
  namespaces.accept('*/xml').get()
 
.. autoclass:: guernsey.filters.ContentMd5Filter
   :members:

.. autoclass:: guernsey.filters.GzipContentEncodingFilter
   :members:

