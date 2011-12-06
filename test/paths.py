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

    def testTemplatedResource(self):
        c = Client.create()
        p = dict(service='addressbook', resource='person', id='simon', view='card')
        r = c.resource('http://example.com/{service}/{resource}/{id}', p)
        self.assertEquals("http://example.com/addressbook/person/simon", r.url)

    def testBadTemplatedResource(self):
        p = dict(service='addressbook', id='simon', view='card')
        c = Client.create()
        try:
            r = c.resource('http://example.com/{service}/{resource}/{id}', p)
            self.fail('"foo" should have failed because of missing template key')
        except KeyError:
            print 'checking template check - OK'
        

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

    def testSubResourceMethod(self):
        c = Client.create()
        r = c.resource("http://example.com/base")
        self.assertEquals("http://example.com/base", r.url)

        r = r.sub_resource("add1/")
        self.assertEquals("http://example.com/base/add1/", r.url)

        r = r.sub_resource("add2/")
        self.assertEquals("http://example.com/base/add1/add2/", r.url)

        r = r.sub_resource("add3/")
        self.assertEquals("http://example.com/base/add1/add2/add3/", r.url)

        try:
            r = r.sub_resource("#add4")
            self.fail('Should not allow fragments in sub_resource values')
        except ValueError:
            pass

        r = r.path("#add4")
        self.assertEquals("http://example.com/base/add1/add2/add3/#add4", r.url)

        try:
            r = r.sub_resource("?q=my+query")
            self.fail('Should not allow queries in sub_resource values')
        except ValueError:
            pass

        r = r.query_params({"q": "my query", "return": "std", "page": 1})
        self.assertEquals("http://example.com/base/add1/add2/add3/?q=my+query&return=std&page=1", r.url)

        r = r.query_params({"format": "json"})
        self.assertEquals("http://example.com/base/add1/add2/add3/?q=my+query&return=std&page=1&format=json", r.url)

        r = r.sub_resource("/add5/")
        self.assertEquals("http://example.com/base/add1/add2/add3/add5/?q=my+query&return=std&page=1&format=json", r.url)

