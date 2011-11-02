import logging, unittest

from guernsey import Client
from guernsey.filters import *

FORMAT = '%(asctime)-15s %(levelname)s %(thread)d %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

class TestBuiltinFilters(unittest.TestCase):

    def testGzipFilter(self):
        client = Client.create()
        namespaces = client.resource('http://www.amazon.com')
        namespaces.add_filter(GzipContentEncodingFilter())
        response = namespaces.accept('*/*').get()
        print namespaces.headers
        print response.headers
        print response.entity

    def testLoggingFilter(self):
        client = Client.create()
        namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/')
        namespaces.add_filter(LoggingFilter('TestFilterLogging'))
        response = namespaces.accept('*/xml').get()
        print response.entity
