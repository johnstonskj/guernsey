#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

from datetime import datetime
from email.utils import parsedate
import copy, logging, mimetools, types, urllib, urllib2, urlparse

from guernsey.entities import *

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

class Filterable(object):
    """ Base class for :class:`Client` and :class:`WebResource` which 
        provides the common implementation of a filter list. Note that
        each :class:`WebResource` when constructed will copy its initial
        filters from the client used to create it.
    """
    def __init__(self):
        self.filters = []

    def add_filter(self, filter):
        """ add_filter(filter) -> WebResource
            Add a filter to the chain for this resource, note that filters
            are always added to the head of the chain, so effectively the
            chain acts as a stack.
        """
        if not self.is_filter_present(filter):
            self.filters.insert(0, filter)
        return self

    def head_filter(self):
        """ head_filter() -> ClientFilter
            Return the first filter in the filter chain defined for this
            resource. 

            Note that Guernsey copies the resource's filter chain
            to the :class:`ClientRequest` when the request is handled and
            so this only works against the chain before it is copied to 
            the request.
        """
        if len(self.filters) > 0:
            return self.filters[0]
        else:
            return self.client.default_filter

    def is_filter_present(self, filter):
        """ is_filter_present(filter) -> boolean
            Returns ``True`` if the specified filter is in the chain for
            this resource.

            Note that Guernsey copies the resource's filter chain
            to the :class:`ClientRequest` when the request is handled and
            so this only works against the chain before it is copied to 
            the request.
        """
        return len([f for f in self.filters if f == filter]) > 0
        return self

    def remove_filter(self, filter):
        """ remove_filter(filter) -> WebResource
            Remove the identified filter from the filter chain for this
            resource.

            Note that Guernsey copies the resource's filter chain
            to the :class:`ClientRequest` when the request is handled and
            so this only works against the chain before it is copied to 
            the request.
        """
        self.filters.remove(filter)
        return self

class Client(Filterable):
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
        self.filters = []
        self.entity_classes = [JsonReader(), JsonWriter()]
        self.actual_client = ExecClientFilter()

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

    def parse_entity(self, client_response):
        for reader in self.entity_classes:
            if hasattr(reader, 'is_readable') and reader.is_readable(client_response.type):
                client_response.parsed_entity = reader.read(client_response.entity, client_response.type)
                break
        return client_response

    def write_entity(self, client_request):
        for writer in self.entity_classes:
            if hasattr(writer, 'is_writable') and writer.is_writable(client_request.entity, client_request.type):
                fh = StringIO.StringIO()
                writer.write(client_request.entity, client_request.type, fh)
                client_request.entity = fh.getvalue()
                break
        return client_response
        pass

    def add_basic_auth(realm, uri, user, passwd):
        global auth_handler
        auth_handler.add_password(realm, uri, user, passwd)

    @classmethod
    def create(cls, config=None, default_filters=None):
        """ Client.create(config) -> Client
            Create a new client instance, this is the primary entry point
            for the library.
        """
        return Client(config)

class ClientResponse(object):
    """ This represents the response from a server based on some request.
        This is commonly returned from one of the methods ``get``, ``head``,
        ``post``, ``delete``, ``options`` or ``handle`` on the 
        :class:`WebResource` class.
        
        The class supports the following data members.

        * ``client`` - the client used to configure this response.
        * ``resource`` - the resource used to initiate this response.
        * ``url``- the URL of the resource retrieved, note that this may be 
          different from the value requested if redirects were followed..
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
        self.client.parse_entity(self)

class WebResource(Filterable):
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
        self.filters = client.filters
        self.headers = {}
        self.req_entity = None

    def clone(self):
        """ clone() -> WebResource
            This will return a copy of the current resource with no shared data,
            specifically will copy ``url``, ``filters``, ``headers`` and 
            ``req_entity``.
        """
        r2 = WebResource(self.url, self.client)
        r2.filters = self.filters[:]
        r2.headers = self.headers.copy()
        r2.req_entity = copy.deepcopy(self.req_entity)
        return r2

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

    def add_header(self, name, value, append=False):
        """ add_header(name, value, append=False) -> WebResource
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
            Add a MIME content type to the list of values in the 
            HTTP ``Accepts`` request header, note that the quality
            parameter is optional but should be a simple decimal
            value.
        """
        if not quality is None:
            content_type = "%s; q=%s" % (content_type, quality)
        self.add_header('Accept', content_type, True)
        return self

    def accept_encoding(self, encoding):
        """ accept_encoding(encoding) -> WebResource
            Add to the list of values in the HTTP ``Accept-Encoding`` 
            request header.
        """
        self.add_header('Accept-Language', language, True)
        return self

    def accept_language(self, language):
        """ accept_language(language) -> WebResource
            Add to the list of values in the HTTP ``Accept-Language`` 
            request header.
        """
        self.add_header('Accept-Language', language, True)
        return self

    def encoding(self, encoding):
        """ encoding(encoding) -> WebResource
            Set the value of the HTTP ``Content-Encoding`` request header.
        """
        self.add_header('Content-Type', content_type)
        return self

    def language(self, language):
        """ language(language) -> WebResource
            Set the value of the HTTP ``Content-Language`` request header.
        """
        self.add_header('Content-Type', content_type)
        return self

    def type(self, content_type):
        """ type(content_type) -> WebResource
            Set the value of the HTTP ``Content-Type`` request header.
        """
        self.add_header('Content-Type', content_type)
        return self

    def entity(self, req_entity):
        """ entity() -> data
            Set the data to be sent to the REST service as the entity body
            with this request.
        """
        self.req_entity = req_entity

    def get(self):
        """ get() -> ClientResponse
            Perform a GET against the resource associated with the URL
            of this :class:`WebResource`.
        """
        request = ClientRequest(self, 'GET')
        return self.handle(request)

    def head(self):
        """ head() -> ClientResponse
            Perform a HEAD against the resource associated with the URL
            of this :class:`WebResource`.
        """
        request = ClientRequest(self, 'HEAD')
        return self.handle(request)

    def put(self, entity=None):
        """ put(entity=None) -> ClientResponse
            Perform a PUT against the resource associated with the URL
            of this :class:`WebResource`.
        """
        if not entity is None:
            self.req_entity = entity
        request = ClientRequest(self, 'PUT')
        return self.handle(request)

    def post(self, entity=None):
        """ post(entity=None) -> ClientResponse
            Perform a POST against the resource associated with the URL
            of this :class:`WebResource`.
        """
        if not entity is None:
            self.req_entity = entity
        request = ClientRequest(self, 'POST')
        return self.handle(request)

    def delete(self):
        """ delete() -> ClientResponse
            Perform a DELETE against the resource associated with the URL
            of this :class:`WebResource`.
        """
        request = ClientRequest(self, 'DELETE')
        return self.handle(request)

    def options(self):
        """ options() -> ClientResponse
            Perform an OPTIONS against the resource associated with the URL
            of this :class:`WebResource`.
        """
        request = ClientRequest(self, 'OPTIONS')
        return self.handle(request)

    def handle(self, client_request):
        """ handle(client_request) -> ClientResponse
            This method is where we actually process a client request and 
            return the client response. This method will invoke all the
            filters defined for this resource and will execute the HTTP
            logic at the end of the filter chain before returning.
        """
        client_request.set_filters(self.filters + [self.client.actual_client]);
        final_response = client_request.filters[0].handle(client_request)
        return final_response

    def debug(self):
        return "<Web Resource '%s' %s>" % (self.url, repr(self.headers))

    def __str__(self):
        return "<Web Resource %s>" % self.url


class ClientRequest(object):
    """ This represents the request to be made to the REST service.

        The class supports the following data members.

        * ``method`` - the HTTP method to use for this request.
        * ``url`` - the request URL.
        * ``resource`` - the originating resource itself.
    """
    def __init__(self, resource, method):
        """ ClientRequest(resource, method) -> ClientRequest
        """
        self.resource = resource
        self.method = method
        self.url = resource.url
        self.filters = []

    def set_filters(self, filters):
        self.filters = filters

    def next_filter(self, filter):
        """ next_filter(filter) -> ClientFilter
            This will return the next filter, after ``filter``,  in the
            filter chain for this request. Note that the filter chain
            is copied from the resource when the request is created to
            ensure it cannot be changed.
        """
        next = self.filters.index(filter)+1
        if next > len(self.filters):
            return self.client.default_filter
        else:
            return self.filters[next]

class ClientFilter(object):
    """ A Filter can be associated with a :class:`WebResource` object and
        will be called for each request made against the resource. The
        pattern is that the calls are nested, so the first filter has
        a chance to modify the request object before invoking the next
        filter in the chain which returns its response. The response may
        then be modified before returning to the previous filter. This 
        model allows for a single filter to affect both request and 
        response while ensuring it is placed at the same location in the
        chain for both operations.
    """
    def handle(self, client_request):
        """ handle(client_request) -> ClientResponse
            Process the request and response as you need to. You must
            ensure that you call ``handle()`` on the next filter in 
            the chain from ``client_request.next_filter(self)`` so that
            the chain remains unbroken.
        """
        return client_request.next_filter(self).handle(client_request)

class ExecClientFilter(ClientFilter):
    """ This class actually implements the HTTP client itself, it is
        styled as a filter and guaranteed to be the last filter executed
        as it does not pass on the request to any next filter.
    """
    def handle(self, client_request):
        """ handle(client_request) -> ClientResponse
            This is where the real HTTP stuff happens.
        """ 
        if client_request.method in ['GET', 'POST']:
            request = urllib2.Request(url=client_request.url, data=client_request.resource.req_entity)
        else:
            request = RequestWithMethod(client_request.method, url=client_request.url, data=client_request.resource.req_entity)
        for k, v in client_request.resource.headers.iteritems():
            request.add_header(k, v)
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            logger = logging.getLogger('guernsey')
            if hasattr(e, 'reason'):
                logger.error('We failed to reach a server. Reason: ', e.reason)
            elif hasattr(e, 'code'):
                logger.error('The server couldn\'t fulfill the request. Status code: ', e.code)
            return ClientResponse(client_request.resource, e, client_request.resource.client)
        else:
            return ClientResponse(client_request.resource, response, client_request.resource.client)

logging.getLogger('guernsey').debug('Initializing password manager')
auth_handler = urllib2.HTTPBasicAuthHandler()
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)
