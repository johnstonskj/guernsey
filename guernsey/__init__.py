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
        """ RequestWithMethod(method, args, kwargs) -> object
            Construct a new request for urllib2 but with a specified
            HTTP method.
        """
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        """ get_method() -> string
            Return the method provided in the initializer.

            :rtype: string
        """
        return self._method

class Filterable(object):
    """ Base class for :class:`Client` and :class:`WebResource` which 
        provides the common implementation of a filter list. Note that
        each :class:`WebResource` when constructed will copy its initial
        filters from the client used to create it.

        The class supports the following data members.

        * ``filters`` - the list of filters to execute.
    """
    def __init__(self):
        self.filters = []

    def add_filter(self, filter):
        """ add_filter(filter) -> Filterable
            Add a filter to the chain for this resource, note that filters
            are always added to the head of the chain, so effectively the
            chain acts as a stack.

            :type filter: :class:`ClientFilter`
            :param filter: a new filter to add to the list of filters on 
                this object. Note that filters may only be added once.
            :rtype: :class:`Filterable`
        """
        if not self.is_filter_present(filter):
            self.filters.insert(0, filter)
        return self

    def head_filter(self):
        """ head_filter() -> ClientFilter
            Return the first filter in the filter chain defined for this
            object. 

            :rtype: :class:`ClientFilter`
        """
        if len(self.filters) > 0:
            return self.filters[0]
        else:
            return self.client.default_filter

    def is_filter_present(self, filter):
        """ is_filter_present(filter) -> boolean
            Returns ``True`` if the specified filter is in the chain for
            this object.

            :type filter: :class:`ClientFilter`
            :param filter: the filter to check for.
            :rtype: Boolean
        """
        return len([f for f in self.filters if f == filter]) > 0
        return self

    def remove_filter(self, filter):
        """ remove_filter(filter) -> Filterable
            Remove the identified filter from the filter chain for this
            object.

            :type filter: :class:`ClientFilter`
            :param filter: the filter to remove from the list of filters
                for this object.
            :rtype: :class:`Filterable`
        """
        self.filters.remove(filter)
        return self

class Client(Filterable):
    """ This is the root object that a REST client interacts with, it is
        responsible for setting up the connection environment and holds
        shared properties used by resource actions. Instances should only
        be created with the :py:func:`create` class method.

        Also, note that the default client will also include an HTTP basic
        authentication handler which can be configured with user
        credentials using the :py:func:`add_basic_auth` method.

        The class supports the following data members.

        * ``config`` - the configuration properties provided on construction.
        * ``entity_classes`` - the set of EntityReader and EntityWriter 
          objects used to marshall objects to/from Python.
        * ``filters`` - the default set of filters used to handle actual
          request/response objects.
    """
    def __init__(self, config):
        """ Client(config)
            A caller should not instantiate a Client object directly, 
            they should only use Client.create()

            :type config: dict
            :param config: a dictionary containing any overridable 
                property values.
        """
        if type(config) == types.DictType:
            self.config = config
        else:
            self.config = {}
        self.filters = []
        self.entity_classes = [JsonReader(), JsonWriter(), XmlReader(), XmlWriter()]
        logging.getLogger('guernsey').debug('Initializing password manager')
        self.auth_handler = urllib2.HTTPBasicAuthHandler()
        self.opener = urllib2.build_opener(self.auth_handler)
        self.actual_client = ExecClientFilter(self.opener)

    def resource(self, url, parameters=None):
        """ resource(url, parameters=None) -> WebResource
            This will construct a new :class:`WebResource` with the specified URL.

            :type url: string
            :param url: the URL for the new resource, this MUST be an absolute URL.

            :type parameters: dict
            :param parameters: If ``parameters`` is specified then treat the
                ``url`` as a template containing strings of the form "{key}" to be 
                replaced with values from the dictionary.
            :rtype: :class:`WebResource`
        """
        if isinstance(parameters, dict):
            url = url.replace('{', '%(').replace('}', ')s')
            url = url % parameters
        return WebResource(url, self)

    def parse_http_date(self, s):
        """ parse_http_date(string) -> datetime
            Return a datetime value parsed from the standard HTTP Date/Time 
            representation.

            :type s: string
            :param s: A string representation of a date/time value.
            :rtype: datetime.datetime
        """
        if s is None:
            return None
        return datetime(*parsedate(s)[:6])

    def parse_entity(self, client_response):
        """ parse_entity(client_response) -> ClientResponse
            Parse the data in the response from the server using all the
            configured entity class handlers. Will return a new response
            with any modification, usually this only sets the value of
            the ``parsed_entity`` property.

            :type client_response: :class:`ClientResponse`
            :param client_response: The response from the server itself.
            :rtype: :class:`ClientResponse`
        """
        client_response.parsed_entity = None
        for reader in self.entity_classes:
            if hasattr(reader, 'is_readable') and not client_response.type is None and reader.is_readable(client_response.type):
                client_response.parsed_entity = reader.read(client_response.entity, client_response.type)
                break
        return client_response

    def write_entity(self, client_request):
        """ write_entity(client_request) -> ClientRequest
            Write the Python data in the request entity using all the
            configured entity class handlers.

            :type client_request: :class:`ClientRequest`
            :param client_request: the request to modify before sending
                to the server.
            :rtype: :class:`ClientRequest`
        """
        for writer in self.entity_classes:
            if hasattr(writer, 'is_writable') and not client_request.entity is None and not client_request.type is None and writer.is_writable(client_request.entity, client_request.type):
                fh = StringIO.StringIO()
                writer.write(client_request.entity, client_request.type, fh)
                client_request.entity = fh.getvalue()
                break
        return client_response
        pass

    def add_basic_auth(realm, url, user, passwd):
        """ add_basic_auth(realm, url, user, passwd) 
            Add the user credentials to the password manager configured
            for this client.

            :type realm: string
            :param realm: The HTTP realm that scopes the authentication.
            :type url: string
            :param url: The URL that scopes the authentication.
            :type user: string
            :param user: The user name to authenticate.
            :type passwd: string
            :param passwd: The user password to authenticate.
        """
        self.auth_handler.add_password(realm, url, user, passwd)

    @classmethod
    def create(cls, config=None, default_filters=None):
        """ Client.create(config) -> Client
            Create a new client instance, this is the primary entry point
            for the library.

            :type config: dict
            :param config: a dictionary of configuration values to override
                the default behavior of the client.
            :rtype: :class:`Client`
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

            :type resource: :class:`WebResource`
            :param resource: The resource that generated this response.
            :param response: The underlying HTTP response.
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

            :type url: string
            :param url: The absolute URL for the resource.
            :type client: :class:`Client`
            :param client: The client object to use for this resource.
            :rtype: WebResource
            :raises: ValueError if the URL is not absolute.
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

            :rtype: :class:`WebResource`
        """
        r2 = WebResource(self.url, self.client)
        r2.filters = self.filters[:]
        r2.headers = self.headers.copy()
        r2.req_entity = copy.deepcopy(self.req_entity)
        return r2

    def query_params(self, params):
        """ query_params(params) -> WebResource
            Construct and return a new :class:`WebResource` whose URL is 
            based upon the current resource URL with the additional query
            parameters specified in the dictionary added.

            :type params: dict
            :params params: A dictionary of query parameters to serialize
                into the resource URL query segment.
            :rtype: WebResource
        """
        check = urlparse.urlparse(self.url, allow_fragments=True)
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
            segment appended, note this is not the same as :py:func:`path`
            which will merge a URL.

            Note that you should not pass in query or fragments into this
            method, any value for ``append_path`` that contains either
            the '#' or '?' character will raise ValueError.

            :type append_path: string
            :param append_path: A path segment to append directly to the 
                current resource URL.
            :rtype: WebResource
            :raises: ValueError if append_path contains '#' or '?'.
        """
        if append_path.find('#') >= 0 or append_path.find('?') >= 0:
            raise ValueError('Invalid value for append_path, appears to include a query or fragment part.')
        url = urlparse.urlparse(self.url, allow_fragments=True)
        if url.path.endswith('/'):
            if append_path.startswith('/'):
                new_path = url.path + append_path[1:]
            else:
                new_path = url.path + append_path
        else:
            if append_path.startswith('/'):
                new_path = url.path + append_path
            else:
                new_path = url.path + '/' + append_path
        new_url = (url.scheme, url.netloc, new_path, url.params, url.query, url.fragment)
        return WebResource(urlparse.urlunparse(new_url), self.client)

    def path(self, relative_path, parameters=None):
        """ path(relative_path, parameters=None) -> WebResource
            Construct and return a new :class:`WebResource` whose URL is 
            based upon the current resource URL with the additional path
            segment resolved against it. This method also takes a 
            parameter dictionary to allow for templated paths.

            :type relative_path: string
            :param relative_path: A path segment to resolve against the current
                resource URL.
            :type parameters: dict
            :param parameters: A dictionary of template parameter values, if
                specified we assume that the relative_path is a template URL.
            :rtype: WebResource
        """
        if isinstance(parameters, dict):
            relative_path = relative_path.replace('{', '%(').replace('}', ')s')
            relative_path = relative_path % parameters
        return WebResource(urlparse.urljoin(self.url, relative_path, True), self.client)

    def add_header(self, name, value, append=False):
        """ add_header(name, value, append=False) -> WebResource
            Add a custom header to the resource, all headers will be sent
            when the request for this resource is handled. This method will
            return the current resource.

            :type name: string
            :param name: The name of the header to add.
            :type value: string
            :param value: The value to add for this header.
            :type append: Boolean
            :param append: If ``False`` then replace any existing value for
                this header with the new value; else append to the existing
                value.
            :rtype: WebResource
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

            :type content_type: string
            :param content_type: A MIME type string.
            :type quality: real
            :param quality: A number between 0.0 and 1.0 to indicate the weight
                of the content_type.
            :rtype: WebResource
        """
        if not quality is None:
            content_type = "%s; q=%s" % (content_type, quality)
        self.add_header('Accept', content_type, True)
        return self

    def accept_encoding(self, encoding):
        """ accept_encoding(encoding) -> WebResource
            Add to the list of values in the HTTP ``Accept-Encoding`` 
            request header.

            :type encoding: string
            :param encoding: An encoding value to add.
            :rtype: WebResource
        """
        self.add_header('Accept-Language', language, True)
        return self

    def accept_language(self, language):
        """ accept_language(language) -> WebResource
            Add to the list of values in the HTTP ``Accept-Language`` 
            request header.

            :type language: string
            :param language: A language value to add.
            :rtype: WebResource
        """
        self.add_header('Accept-Language', language, True)
        return self

    def encoding(self, encoding):
        """ encoding(encoding) -> WebResource
            Set the value of the HTTP ``Content-Encoding`` request header.

            :type encoding: string
            :param encoding: An encoding value to add.
            :rtype: WebResource
        """
        self.add_header('Content-Type', content_type)
        return self

    def language(self, language):
        """ language(language) -> WebResource
            Set the value of the HTTP ``Content-Language`` request header.

            :type language: string
            :param language: A language value to add.
            :rtype: WebResource
        """
        self.add_header('Content-Type', content_type)
        return self

    def type(self, content_type):
        """ type(content_type) -> WebResource
            Set the value of the HTTP ``Content-Type`` request header.

            :type content_type: string
            :param content_type: A MIME type value to add.
            :rtype: WebResource
        """
        self.add_header('Content-Type', content_type)
        return self

    def entity(self, req_entity):
        """ entity() -> WebResource
            Set the data to be sent to the REST service as the entity body
            with this request.

            :type req_entity: string
            :param req_entity: An Entity type value to add.
            :rtype: WebResource
        """
        self.req_entity = req_entity
        return self

    def get(self):
        """ get() -> ClientResponse
            Perform a GET against the resource associated with the URL
            of this :class:`WebResource`.

            :rtype: :class:`ClientResponse`
        """
        request = ClientRequest(self, 'GET')
        return self.handle(request)

    def head(self):
        """ head() -> ClientResponse
            Perform a HEAD against the resource associated with the URL
            of this :class:`WebResource`.

            :rtype: :class:`ClientResponse`
        """
        request = ClientRequest(self, 'HEAD')
        return self.handle(request)

    def put(self, entity=None):
        """ put(entity=None) -> ClientResponse
            Perform a PUT against the resource associated with the URL
            of this :class:`WebResource`.

            :type entity: string
            :param entity: The entity to send to the server, if not specified
                any value set by the :py:func:`entity` will be used.
            :rtype: :class:`ClientResponse`
        """
        if not entity is None:
            self.req_entity = entity
        request = ClientRequest(self, 'PUT')
        return self.handle(request)

    def post(self, entity=None):
        """ post(entity=None) -> ClientResponse
            Perform a POST against the resource associated with the URL
            of this :class:`WebResource`.

            :type entity: string
            :param entity: The entity to send to the server, if not specified
                any value set by the :py:func:`entity` will be used.
            :rtype: :class:`ClientResponse`
        """
        if not entity is None:
            self.req_entity = entity
        request = ClientRequest(self, 'POST')
        return self.handle(request)

    def delete(self):
        """ delete() -> ClientResponse
            Perform a DELETE against the resource associated with the URL
            of this :class:`WebResource`.

            :rtype: :class:`ClientResponse`
        """
        request = ClientRequest(self, 'DELETE')
        return self.handle(request)

    def options(self):
        """ options() -> ClientResponse
            Perform an OPTIONS against the resource associated with the URL
            of this :class:`WebResource`.

            :rtype: :class:`ClientResponse`
        """
        request = ClientRequest(self, 'OPTIONS')
        return self.handle(request)

    def handle(self, client_request):
        """ handle(client_request) -> ClientResponse
            This method is where we actually process a client request and 
            return the client response. This method will invoke all the
            filters defined for this resource and will execute the HTTP
            logic at the end of the filter chain before returning.

            :type client_request: :class:`ClientRequest`
            :param client_request: The request to make to the server.
            :rtype: :class:`ClientResponse`
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

            :type filter: :class:`ClientFilter`
            :param filter: The current filter.
            :rtype: :class:`ClientFilter`
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

        The basic structure of a filter is therefore::

          class MyFilter(ClientFilter):
              def handle(self, client_request):
                  # look at the request
                  # modify the request if needed
                  rsp = client_request.next_filter(self).handle(client_request)
                  # look at the response
                  # modify the response if needed
                  return rsp
    """
    def handle(self, client_request):
        """ handle(client_request) -> ClientResponse
            Process the request and response as you need to. You must
            ensure that you call ``handle()`` on the next filter in 
            the chain from ``client_request.next_filter(self)`` so that
            the chain remains unbroken.

            :type client_request: :class:`ClientRequest`
            :param client_request: The request to process, pass this to 
                the next filter in the chain.
            :rtype: :class:`ClientResponse`
        """
        return client_request.next_filter(self).handle(client_request)

class ExecClientFilter(ClientFilter):
    """ This class actually implements the HTTP client itself, it is
        styled as a filter and guaranteed to be the last filter executed
        as it does not pass on the request to any next filter.
    """
    def __init__(self, opener):
        self.opener = opener

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
            response = self.opener.open(request)
        except urllib2.URLError, e:
            logger = logging.getLogger('guernsey')
            if hasattr(e, 'reason'):
                logger.error('We failed to reach a server. Reason: %s' % e.reason)
            elif hasattr(e, 'code'):
                logger.error('The server couldn\'t fulfill the request. Status code: %d' % e.code)
            return ClientResponse(client_request.resource, e, client_request.resource.client)
        else:
            return ClientResponse(client_request.resource, response, client_request.resource.client)

