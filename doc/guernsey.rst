Guernsey REST Client Module
---------------------------

.. automodule:: guernsey

The Guernsey REST client provides a hybrid object/functional API to
access RESTful services from Python. The inspiration comes from the
Java Jersey API
(see `Jersey Client API <http://jersey.java.net/nonav/documentation/latest/user-guide.html#client-api>`_), 
although it does not slavishly copy Java idioms in favor of a more
Python-like interface.

Consider the following simple example. ::

   from guernsey import Client

   client = Client.create()
   resource = client.resource('http://www.thomas-bayer.com/sqlrest/')
   resource.accept('*/xml')
   namespaces = resource.get()

In this case we have a fairly simple and obvious interaction, we create
a new client object, from which we create a new resource object, then
we tell the resource what representations we are willing to accept and
fetch the resource into a local response object using ``get()``.

Additionally, the API supports a more functional style, nearly all the
methods on ``WebResource`` return either the same or a new instance of
``WebResource`` and so can be chained together. The following example
demonstrates how this can be used to construct more compact request
code. ::

   client = Client.create()
   namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/').accept('*/xml').get()
   customers = namespaces.resource.path('CUSTOMERS/').accept('*/xml').get()
   customer = customers.resource.path('../CUSTOMER/22022010').accept('*/xml').get()

Primary Client Classes
***********************

The following classes make up the standard, basic, API for retrieving
and updating REST resources. The :class:`Client` class is used to 
store common configuration details for HTTP connections, the 
:class:`WebResource` is used to manage actions against a single URL,
and finally the :class:`ClientResponse` wraps up the HTTP response
and decodes it into a more meaningful form.

.. autoclass:: guernsey.Client
   :members:
   :inherited-members:

.. autoclass:: guernsey.WebResource
   :members:
   :inherited-members:

.. autoclass:: guernsey.ClientResponse
   :members:

Classes for Filtering
*********************

The Guernsey API, like Jersey, provides a filtering capability to
allow components to amend the request and response for any 
:class:`WebResource` by adding filters to the resource before it
is used. The classes below are the primary API for implementing
a new filter and receiving the request itself for processing.

The pattern for implementing a filter is::

  class MyFilter(ClientFilter):

      def handle(self, client_request):
          client_request = client_request.add_header('Accept-Encoding', 'GZip')
          client_response = client_request.next_filter(self).handle(client_request)
          if client.response.encoding == 'gzip':
              self.decode_gzip(client_response)
          return client_response

#. First, perform any modification on the request itself, in this
   case add a new request header.
#. Invoke the next handler in the chain, in this case by calling
   the ``next_handler`` method on the :class:`ClientRequest`.
#. Now process any information in the response, modifying it as
   necessary.
#. Finally, return the response object to the previous handler
   in the chain.

Filters are added and removed from a particular :class:`WebResource`
using the ``add_filter`` and ``remove_filter`` methods. Additionally
a resource will have a pre-configured list of filters when constructed.

See also the :doc:`filters` topic for documentation on standard
filters..

.. autoclass:: guernsey.ClientFilter
   :members:

.. autoclass:: guernsey.ClientRequest
   :members:

