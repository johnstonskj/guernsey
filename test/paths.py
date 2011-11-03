#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

import unittest

from guernsey import Client

class TestPathConstruction(unittest.TestCase):

    def testBadPath(self):
        c = Client.create()
        try:
            r = c.resource('foo')
            self.fail('"foo" should have failed as its not a valid URL')
        except ValueError:
            print 'checking URL check - OK'

    def testPathMethod(self):
        c = Client.create()
        r = c.resource("http://example.com/base")
        self.assertEquals("http://example.com/base", r.url)

        r = r.path("add1/")
        self.assertEquals("http://example.com/add1/", r.url)

        r = r.path("add2/")
        self.assertEquals("http://example.com/add1/add2/", r.url)

        r = r.path("add3/")
        self.assertEquals("http://example.com/add1/add2/add3/", r.url)

        r = r.path("#add4")
        self.assertEquals("http://example.com/add1/add2/add3/#add4", r.url)

        r = r.query_params({"q": "my query", "return": "std", "page": 1})
        self.assertEquals("http://example.com/add1/add2/add3/?q=my+query&return=std&page=1", r.url)

        r = r.query_params({"format": "json"})
        self.assertEquals("http://example.com/add1/add2/add3/?q=my+query&return=std&page=1&format=json", r.url)

        r = r.path("/add5/")
        self.assertEquals("http://example.com/add5/", r.url)

        r = r.path("#add6")
        self.assertEquals("http://example.com/add5/#add6", r.url)

