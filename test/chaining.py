import unittest

from guernsey import Client

class TestMethodChaining(unittest.TestCase):

    def testSimpleRequest(self):
        c = Client.create()
        r = c.resource("http://example.com/base").path("1").accept("text/json").accept("text/xml", 0.5)
        print r.debug()

    def testServiceCall(self):
        c = Client.create()
        r = c.resource("http://rsp-core-services-na.amazon.com/services/marketplaces").accept("application/json")
        v = r.get()
        print v.entity
        print v.url
        print str(v.status) + " " + v.reason_phrase
        print v.headers
        print v.parsed_entity

