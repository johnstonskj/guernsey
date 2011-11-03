#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

import logging, StringIO, unittest

from guernsey import Client
from guernsey.filters import *

stream = StringIO.StringIO()
FORMAT = '%(asctime)-15s %(levelname)s %(thread)d %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG, stream=stream)

class TestBuiltinFilters(unittest.TestCase):

    def testGzipFilter(self):
        client = Client.create()
        namespaces = client.resource('http://www.amazon.com')
        namespaces.add_filter(GzipContentEncodingFilter())
        response = namespaces.accept('*/*').get()
        self.assertEquals('gzip', namespaces.headers.get('accept-encoding', ''))
        self.assertEquals('gzip', response.headers.get('content-encoding', ''))
        self.assertTrue(response.entity.find('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"') > 0)

    def testLoggingFilter(self):
        client = Client.create()
        namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/')
        namespaces.add_filter(LoggingFilter('TestFilterLogging'))
        response = namespaces.accept('*/xml').get()
        log_text = stream.getvalue()
        self.assertTrue(log_text.find('GET http://www.thomas-bayer.com/sqlrest/') > 0)
        self.assertTrue(log_text.find('http://www.thomas-bayer.com/sqlrest/ 200 OK') > 0)
