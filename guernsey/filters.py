#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

import gzip, logging, hashlib, StringIO

from guernsey import ClientFilter

class GzipContentEncodingFilter(ClientFilter):
    """ This filter does two things, on the request side it will add the
        standard HTTP ``Accept-Encoding`` header with the value ``gzip``.
        The result is that a server should respond with a compressed entity
        and the response header ``Content-Encoding`` also set to ``gzip``.
        If the response does include the content encoding header the 
        filter will uncompress the data and replace the ``entity`` value
        in the :class:`ClientResponse` object accordingly.
    """
    def handle(self, client_request):
        client_request.resource.headers['accept-encoding'] = 'gzip'
        client_response = client_request.next_filter(self).handle(client_request)
        if client_response.headers['content-encoding'] == 'gzip':
            data = StringIO.StringIO(client_response.entity)
            encoded = gzip.GzipFile(fileobj=data, mode='rb')
            entity = encoded.read()
            encoded.close()
            client_response.entity = entity
        return client_response

class ContentMd5Filter(ClientFilter):
    """ This filter does two things, on the request side, if an entity is 
        present it will calculate an MD5 hash for the entity and include
        a ``Content-MD5`` HTTP header. On the response side, if the response
        includes this header the filter will calculate a new hash of the 
        entity it has been given and will compare the two values. If the 
        values do not match it will raise a :class:`ValueError` exception.
    """
    def handle(self, client_request):
        if not client_request.entity is None:
            hash = hashlib.md5()
            hash.update(client_request.entity)
            client_request.add_header('Content-MD5', hash.hexdigest())
        client_response = client_request.next_filter(self).handle(client_request)
        if not client_response.headers['content-md5'] is None:
            hash = hashlib.md5()
            hash.update(client_response.entity)
            if hash.hexdigest() != client_response.headers['content-md5']:
                raise ValueError('MD5 hash mimatch')
        return client_response

class LoggingFilter(ClientFilter):
    """ This filter will log requests and responses, it uses the standard
        Python ``logging`` module and has to be configured with the 
        following parameters on construction.

        * ``log_name`` - the name to use as the logger name when calling
          ``logging.getLogger()``; default is 'GuernseyClient'.
        * ``log_level`` - the level to use when logging; default is
          ``logging.INFO``.
    """
    def __init__(self, log_name=None, log_level=None):
        """ LoggingFilter(log_name=None, log_level=None) -> LoggingFilter
            This will construct a 
        """
        if log_name is None:
            self.log_name = 'GuernseyClient'
        else:
            self.log_name = log_name
        if log_level is None:
            self.log_level = logging.INFO
        else:
            self.log_level = log_level

    def handle(self, client_request):
        logger = logging.getLogger(self.log_name)
        logger.info(client_request.method + ' ' + client_request.url)
        client_response = client_request.next_filter(self).handle(client_request)
        logger.info(client_response.url + ' ' + 
            str(client_response.status)+ ' ' + 
            client_response.reason_phrase)
        return client_response

