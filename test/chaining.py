#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

import unittest

from guernsey import Client

class TestMethodChaining(unittest.TestCase):

    def testSimpleRequest(self):
        c = Client.create()

        r = c.resource('http://example.com/base/').path('1').accept('text/json').accept('text/xml', 0.5)
        self.assertEquals('http://example.com/base/1', r.url)
        self.assertEquals('text/json, text/xml; q=0.5', r.headers['Accept'])

    def testServiceCall(self):
        client = Client.create()

        namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/').accept('*/xml').get()
        self.assertEquals('http://www.thomas-bayer.com/sqlrest/', namespaces.url)
        self.assertEquals('*/xml', namespaces.resource.headers['Accept'])
        self.assertEquals('application/xml', namespaces.headers['content-type'])

        customers = namespaces.resource.path('CUSTOMERS/').accept('*/xml').get()
        self.assertEquals('http://www.thomas-bayer.com/sqlrest/CUSTOMERS/', customers.url)
        self.assertEquals('*/xml', customers.resource.headers['Accept'])
        self.assertEquals('application/xml', customers.headers['content-type'])

        customer = customers.resource.path('../CUSTOMER/22022010').accept('*/xml').get()
        self.assertEquals('http://www.thomas-bayer.com/sqlrest/CUSTOMER/22022010', customer.url)
        self.assertEquals('*/xml', customer.resource.headers['Accept'])
        self.assertEquals('application/xml', customer.headers['content-type'])
