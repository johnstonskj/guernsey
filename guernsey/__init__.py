#
# Guernsey REST client package, based on the Java Jersey client.
#

from datetime import datetime
from email.utils import parsedate
import mimetools, types, urllib, urllib2, urlparse
try:
    import json
except:
    json = None

class RequestWithMethod(urllib2.Request):
    """ This simple class is used to allow us to use the standard urllib2
        module to make PUT, POST and DELETE methods. This requires a pretty
        simple addition so that we can use this efficiently.
    """
    def __init__(self, method, *args, **kwargs):
        """ request = RequestWithMethod('PUT', url=_url) """
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        """ return the method provided in the initializer """
        return self._method

class Client(object):
    """ This is the root object that a REST client interacts with, it is
        responsible for setting up the connection environment and holds
        shared properties used by resource actions. Instances should only
        be created with the :py:func:`create` class method.
    """
    def __init__(self, config):
        """ Client(config)
            A caller should not instantiate a Client object directly, 
            they should only use Client.create()
        """
        if type(config) == types.DictType:
            self.config = config
        else:
            self.config = {}
        self.default_filters = []

    def resource(self, url):
        """ resource(url) -> WebResource
            This will construct a new :class:`WebResource` with the specified URL.
        """
        return WebResource(url, self)

    def parse_http_date(self, s):
        """ parse_http_date(string) -> datetime
            Return a datetime value parsed from the standard HTTP 
            Date/Time representation.
        """
        if s is None:
            return None
        return datetime(*parsedate(s)[:6])

    @classmethod
    def create(cls, config=None):
        """ Client.create(config) -> Client
            Create a new client instance, this is the primary entry point
            for the library.
        """
        return Client(config)

class ClientRequest(object):
    """ TBD
    """
    pass

class ClientResponse(object):
    """ This represents the response from a server based on some request.
        This is commonly returned from one of the methods ``get``, ``head``,
        ``post``, ``delete``, ``options`` or ``handle`` on the 
        :class:`WebResource` class.
        
        The class supports the following data members.

        * ``client`` - the client used to configure this response.
        * ``resource`` - the resource used to initiate this response.
        * ``url``- the URL of the resource retrieved.
        * ``entity`` - the original entity, as a binary stream, retrieved.
        * ``status`` - the HTTP status code for this response.
        * ``reason_phrase`` - the HTTP reason phrase for this response.
        * ``headers`` - the dictionary of all headers for this response.
        * ``allow`` - the value of the HTTP ``Allow`` response header.
        * ``entity_tag`` - the value of the HTTP ``ETag`` response header.`
        * ``language`` - the value of the HTTP ``Language`` response header.`
        * ``length`` - the value of the HTTP ``Content-Length`` response header.`
        * ``location`` - the value of the HTTP ``Location`` response header.`
        * ``response_date`` - the value of the HTTP ``Date`` response header.`
        * ``type`` - the value of the HTTP ``Content-Type`` response header.`
    """
    def __init__(self, resource, response, client):
        """ ClientResponse(resource, response, client) -> ClientResponse
            construct a new response from the actual underlying HTTP response
            object. Also track the resource that created this response and
            the client.
        """
        self.resource = resource
        self.client = client
        self.entity = response.read()
        self.url = response.geturl()
        if isinstance(response.info(), mimetools.Message):
            self.status = response.getcode()
            self.reason_phrase = response.msg
            self.headers = {}
            for header in response.info().headers:
                self.headers[header[:header.find(':')].lower()] = header[header.find(':')+1:].strip()
            self.allow = self.headers.get('allow', None)
            self.entity_tag = self.headers.get('etag', None)
            self.language = self.headers.get('language', None)
            self.last_modified = client.parse_http_date(self.headers.get('last-modified', None))
            self.length = self.headers.get('content-length', None)
            self.location = self.headers.get('location', None)
            self.response_date = client.parse_http_date(self.headers.get('date', None))
            self.type = self.headers.get('content-type', None)
        if self.type in ['text/json', 'application/json'] and not json is None:
            self.parsed_entity = json.loads(self.entity)
        else:
            self.parsed_entity = None

class ClientFilter(object):
    """ TBD
    """
    def handle(self, client_request, next_filter):
        """ handle(client_request, next_filter) -> ClientResponse
        """
        return None

class WebResource(object):
    """ This is the primary class used to represent a REST resource which a 
        client can interact with. The resource has a URL, is associated
        with a :class:`Client` object used to configure HTTP behavior, and
        allows clients to retrieve, update and delete the resource.

        Note that nearly all methods either return the current, or a new
        instance of :class:`WebResource` which allows a chaining style of
        construction.
    """
    def __init__(self, url, client):
        """ Webresource(URL, client) -> WebResource
            Construct a new WebResource from a client, with the specified
            URL. Resources should not be created directly in this manner,
            rather they should use the ``create`` method on :class:`Client`
            of the :py:func:`path`, :py:func:`sub_resource`, or 
            :py:func:`query_params` methods on an existing resource.
        """
        self.url = url
        check = urlparse.urlparse(url)
        if check.scheme == '' or check.netloc == '':
            raise ValueError('invalid URL value')
        self.client = client
        self.filters = client.default_filters
        self.headers = {}
        self.req_entity = None

    def query_params(self, dictionary):
        """ query_params(dictionary) -> WebResource
            Construct and return a new :class:`WebResource` whose URL is 
            based upon the current resource URL with the additional query
            parameters specified in the dictionary added.
        """
        check = urlparse.urlparse(self.url)
        if check.query == '':
            query_terms = '?' + urllib.urlencode(dictionary)
        else:
            orig_query_terms = urlparse.parse_qsl(check.query)
            new_query_terms = [(k, v) for k,v in dictionary.iteritems()]
            query_terms = '?' + urllib.urlencode(orig_query_terms + new_query_terms)
        new_url = urlparse.urljoin(self.url, query_terms)
        return WebResource(new_url, self.client)

    def sub_resource(self, append_path):
        """ sub_resource(append_path) -> WebResource
            Construct and return a new :class:`WebResource` whose URL is 
            based upon the current resource URL with the additional path
            segment resolved against it. 
        """
        return self.path(append_path)

    def path(self, append_path):
        """ path(append_path) -> WebResource
            Construct and return a new :class:`WebResource` whose URL is 
            based upon the current resource URL with the additional path
            segment resolved against it. 
        """
        return WebResource(urlparse.urljoin(self.url, append_path, True), self.client)

    def header(self, name, value, append=False):
        """ header(name, value, append=False) -> WebResource
            Add a custom header to the resource, all headers will be sent
            when the request for this resource is handled. This method will
            return the current resource.
        """
        if append and name in self.headers:
            self.headers[name] = "%s, %s" % (self.headers[name], value)
        else:
            self.headers[name] = value
        return self
    
    def accept(self, content_type, quality=None):
        """ accept(content_type, quality=None) -> WebResource
        """
        if not quality is None:
            content_type = "%s; q=%s" % (content_type, quality)
        self.header('Accept', content_type, True)
        return self

    def accept_language(self, language):
        """ accept_language(language) -> WebResource
        """
        self.header('Language', language, True)
        return self

    def type(self, content_type):
        """ type(content_type) -> WebResource
        """
        self.header('Content-Type', content_type)
        return self

    def entity(self, req_entity):
        """ entity() -> data
        """
        self.req_entity = req_entity

    def get(self):
        """ get() -> ClientResponse
        """
        return self.execute('GET')

    def head(self):
        """ head() -> ClientResponse
        """
        return self.execute('HEAD')

    def put(self, entity=None):
        """ put(entity=Nont) -> ClientResponse
        """
        self.req_entity = entity
        return self.execute('PUT')

    def post(self, entity=None):
        """ post(entity=None) -> ClientResponse
        """
        self.req_entity = entity
        return self.execute('POST')

    def delete(self):
        """ delete() -> ClientResponse
        """
        return self.execute('DELETE')

    def options(self):
        """ options() -> ClientResponse
        """
        return self.execute('OPTIONS')

    def handle(self, client_request):
        """ handle(client_request) -> ClientResponse
        """
        pass

    def execute(self, method):
        """ execute(method) -> ClientResponse
        """
        # TODO: process filters
        if method in ['GET', 'POST']:
            request = urllib2.Request(url=self.url, data=self.req_entity)
        else:
            request = RequestWithMethod(method, url=self.url, data=self.req_entity)
        for k, v in self.headers.iteritems():
            request.add_header(k, v)
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
            return None
        else:
            return ClientResponse(self, response, self.client)

    def add_filter(self, filter):
        """ add_filter(filter) -> webResource
        """
        if not self.is_filter_present(filter):
            self.filters.append(filter)
        return self

    def get_head_handler(self):
        """ get_head_handler() -> ClientFilter
        """
        if len(self.filters) > 0:
            return self.filters[0]
        else:
            return None

    def is_filter_present(self, filter):
        """ is_filter_present(filter) -> boolean
        """
        return len([f for f in self.filters if f == filter]) > 0
        return self

    def remove_filter(self, filter):
        """ remove_filter(filter) -> WebResource
        """
        self.filters.remove(filter)
        return self

    def debug(self):
        return "<Web Resource '%s' %s>" % (self.url, repr(self.headers))

    def __str__(self):
        return "<Web Resource %s>" % self.url



