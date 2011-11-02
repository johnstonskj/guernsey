Guernsey REST Client Module
---------------------------

.. automodule:: guernsey

Introduction... ::

   from guernsey import Client

   client = Client.create()
   resource = client.resource('http://www.thomas-bayer.com/sqlrest/')
   resource.accept('*/xml')
   namespaces = resource.get()

Additionally, the API supports a chaining style, ... ::

   client = Client.create()
   namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/').accept('*/xml').get()
   customers = namespaces.resource.path('CUSTOMERS/').accept('*/xml').get()
   customer = customers.resource.path('../CUSTOMER/22022010').accept('*/xml').get()

Primary Client Classes
***********************

.. autoclass:: guernsey.Client
   :members:

.. autoclass:: guernsey.WebResource
   :members:

.. autoclass:: guernsey.ClientResponse
   :members:

Classes for Filtering
*********************

.. autoclass:: guernsey.ClientRequest
   :members:

.. autoclass:: guernsey.ClientFilter
   :members:
