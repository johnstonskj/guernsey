# Introduction #

Here are some very simple examples showing how the package is used. More examples in a blog article _[Guernsey REST Client for Python](http://havetocode.blogspot.com/2011/12/guernsey-rest-client-for-python.html)_.


# Get a simple page #

```
from guernsey import Client

client = Client.create()
resource = client.resource('http://www.thomas-bayer.com/sqlrest/')
resource.accept('*/xml')
namespaces = resource.get()
```

or, alternatively you can use the functional model where calls are chained together; each method on the resource will either return the same resource or a new resource and so can be chained in the fashion below.

```
client = Client.create()
namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/').accept('*/xml').get()
customers = namespaces.resource.path('CUSTOMERS/').accept('*/xml').get()
customer = customers.resource.path('../CUSTOMER/22022010').accept('*/xml').get()
```

The final method, either _get_, _head_, _post_, _put_, _delete_ or _options_ will return a response object. In general the only error can come in constructing a new resource with a bad URL, intermediate methods such as _accept_ above generally do not raise exceptions and will return the resource object safely.

# Add a filter #

One feature of the Jersey API is the ability to manage a filter (or handler) chain for a resource. The Guernsey API has simplified this a little, mainly in that Jersey sometimes talks about handlers and sometimes about filters whereas the Guernsey `WebResource` class only talks about filters. Below is an example of the provided `LoggingFilter` in use.

```
client = Client.create()
namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/')
namespaces.add_filter(LoggingFilter('TestFilterLogging'))
response = namespaces.accept('*/xml').get()
```

The package also contains the following filters.

  * `LoggingFilter` - logs the method and URL on request and the status code/reason on the response.
  * `GzipContentEncodingFilter` - adds the correct request headers and deals with compressed responses.
  * `ContentMd5Filter` - adds the correct request headers and validates with hashed responses.