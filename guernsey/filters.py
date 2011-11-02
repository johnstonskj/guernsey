import logging

from guernsey import ClientFilter

class GzipContentEncodingFilter(ClientFilter):
    """ TBD
    """
    def handle(self, client_request):
        return self.response

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
            log_name = 'GuernseyClient'
        else:
            self.log_name = log_name
        if log_level is None:
            log_level = logging.INFO
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

