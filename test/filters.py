import logging, unittest

from guernsey import Client
from guernsey.filters import LoggingFilter

FORMAT = '%(asctime)-15s %(levelname)s %(thread)d %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

class TestBuiltinFilters(unittest.TestCase):

    def testServiceCall(self):
        client = Client.create()
        namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/')
        namespaces.add_filter(LoggingFilter('TestFilterLogging'))
        namespaces.accept('*/xml').get()
