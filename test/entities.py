#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

import logging, StringIO, unittest

from xml.etree.ElementTree import _ElementInterface, Element, ElementTree

from guernsey.entities import *

class TestBuiltinEntityClasses(unittest.TestCase):

    def testJsonReaderIsReadable(self):
        test = JsonReader()
        self.assertTrue(test.is_readable('application/json'))
        self.assertTrue(test.is_readable('text/json'))
        self.assertFalse(test.is_readable('text/xml'))

    def testJsonReaderRead(self):
        test = JsonReader()
        obj = test.read('{}', 'application/json')
        self.assertEqual('{}', repr(obj))

        obj = test.read('[1, 2, 3]', 'application/json')
        self.assertEqual('[1, 2, 3]', repr(obj))

        obj = test.read('{"a": 1, "b": 2, "c": 3}', 'application/json')
        self.assertEqual("{u'a': 1, u'c': 3, u'b': 2}", repr(obj))

    def testJsonWriterIsWriteable(self):
        test = JsonWriter()
        self.assertTrue(test.is_writable({}, 'application/json'))
        self.assertTrue(test.is_writable({}, 'text/json'))
        self.assertFalse(test.is_writable({}, 'text/xml'))

    def testJsonWriterWrite(self):
        test = JsonWriter()

        file = StringIO.StringIO()
        test.write({}, 'application/json', file)
        self.assertEquals('{}', file.getvalue())

        file = StringIO.StringIO()
        test.write({"a": 1, "b": "BB", "c": []}, 'application/json', file)
        self.assertEquals('{"a": 1, "c": [], "b": "BB"}', file.getvalue())

    def testXmlReaderIsReadable(self):
        test = XmlReader()
        self.assertTrue(test.is_readable('application/xml'))
        self.assertTrue(test.is_readable('text/xml'))
        self.assertTrue(test.is_readable('application/atom+xml'))
        self.assertFalse(test.is_readable('text/html'))

    def testXmlReaderRead(self):
        test = XmlReader()
        root = test.read('<Head title="My XML" />', 'application/xml')
        self.assertEquals('Head', root.tag)
        self.assertEquals('My XML', root.attrib['title'])

    def testXmlWriterIsWriteable(self):
        test = XmlWriter()
        tree = ElementTree()
        self.assertTrue(test.is_writable(tree, 'application/xml'))
        self.assertTrue(test.is_writable(tree, 'text/xml'))
        self.assertTrue(test.is_writable(tree, 'application/atom+xml'))
        self.assertFalse(test.is_writable({}, 'application/xml'))
        self.assertFalse(test.is_writable({}, 'text/xml'))
        self.assertFalse(test.is_writable({}, 'application/atom+xml'))
        self.assertFalse(test.is_writable(tree, 'text/html'))

    def testXmlWriterWrite(self):
        test = XmlWriter()

        file = StringIO.StringIO()
        root = Element('Head', {'title': 'My XML'})
        tree = ElementTree(root)
        test.write(tree, 'application/xml', file)
        self.assertEquals('<Head title="My XML" />', file.getvalue())

        file = StringIO.StringIO()
        root = Element('Head', {'title': 'My XML'})
        test.write(root, 'application/xml', file)
        self.assertEquals('<Head title="My XML" />', file.getvalue())
