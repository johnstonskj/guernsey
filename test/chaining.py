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
        r = c.resource("http://example.com/base").path("1").accept("text/json").accept("text/xml", 0.5)
        print r.debug()

    def testServiceCall(self):
        client = Client.create()
        namespaces = client.resource('http://www.thomas-bayer.com/sqlrest/').accept('*/xml').get()
        customers = namespaces.resource.path('CUSTOMERS/').accept('*/xml').get()
        customer = customers.resource.path('../CUSTOMER/22022010').accept('*/xml').get()
