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

    def __init__(self, config):
        if type(config) == types.DictType:
            self.config = config
        else:
            self.config = {}
        self.default_filters = []

    def resource(self, url):
        return WebResource(url, self)

    def parse_http_date(self, s):
        if s is None:
            return None
        return datetime(*parsedate(s)[:6])

    @classmethod
    def create(cls, config=None):
        return Client(config)

class ClientRequest(object):
    pass

class ClientResponse(object):
    def __init__(self, resource, response, client):
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
    def handle(self, client_request, next_filter):
        return None

class LastClientFilter(ClientFilter):
    def __init__(self, response):
        self.response = response

    def handle(self, client_request, next_filter):
        return self.response

class WebResource(object):

    def __init__(self, url, client):
        self.url = url
        check = urlparse.urlparse(url)
        if check.scheme == '' or check.netloc == '':
            raise ValueError('invalid URL value')
        self.client = client
        self.filters = client.default_filters
        self.headers = {}
        self.req_entity = None

    def query_params(self, dictionary):
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
        return self.path(append_path)

    def path(self, append_path):
        return WebResource(urlparse.urljoin(self.url, append_path, True), self.client)

    def header(self, name, value, append=False):
        if append and name in self.headers:
            self.headers[name] = "%s, %s" % (self.headers[name], value)
        else:
            self.headers[name] = value
        return self
    
    def accept(self, content_type, quality=None):
        if not quality is None:
            content_type = "%s; q=%s" % (content_type, quality)
        self.header('Accept', content_type, True)
        return self

    def accept_language(self, language):
        self.header('Language', language, True)
        return self

    def type(self, content_type):
        self.header('Content-Type', content_type)
        return self

    def entity(self, req_entity):
        self.req_entity = req_entity

    def get(self):
        return self.execute('GET')

    def head(self):
        return self.execute('HEAD')

    def put(self, entity=None):
        self.req_entity = entity
        return self.execute('PUT')

    def post(self, entity=None):
        self.req_entity = entity
        return self.execute('POST')

    def delete(self):
        return self.execute('DELETE')

    def options(self):
        return self.execute('OPTIONS')

    def execute(self, method):
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
        if not self.is_filter_present(filter):
            self.filters.append(filter)

    def get_head_handler(self):
        if len(self.filters) > 0:
            return self.filters[0]
        else:
            return None

    def is_filter_present(self, filter):
        return len([f for f in self.filters if f == filter]) > 0

    def remove_filter(self, filter):
        self.filters.remove(filter)

    def debug(self):
        return "<Web Resource '%s' %s>" % (self.url, repr(self.headers))

    def __str__(self):
        return "<Web Resource %s>" % self.url



