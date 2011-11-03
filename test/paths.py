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
            print str(r)
        except ValueError:
            print 'checking URL check - OK'

    def testPathMethod(self):
        c = Client.create()
        r = c.resource("http://example.com/base")
        print str(c)
        print str(r)
        r = r.path("add1/")
        print str(r)
        r = r.path("add2/")
        print str(r)
        r = r.path("add3/")
        print str(r)
        r = r.path("#add4")
        print str(r)
        r = r.query_params({"q": "my+query", "return": "std", "page": 1})
        print str(r)
        r = r.query_params({"format": "json"})
        print str(r)
        r = r.path("/add5/")
        print str(r)
        r = r.path("#add6")
        print str(r)

