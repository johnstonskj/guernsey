#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

import logging

try:
    import json
except:
    json = None
from xml.etree.ElementTree import fromstring, _ElementInterface, ElementTree

logger = logging.getLogger('guernsey')

class EntityReader(object):
    """ An ``EntityReader`` is used to read a raw entity from the
        HTTP response and construct a Python object representation.
    """
    def is_readable(self, content_type):
        """ is_readable(content_type) -> boolean
            Return whether this reader can read an object serialized
            with the specified MIME content type.

            :type content_type: string
            :param content_type: The MIME type of the resource.
            :rtype: Boolean
        """
        return False

    def read(self, entity, content_type):
        """ read(entity, content_type) -> object
            Read and parse the entity and return an object representation.

            :type entity: string
            :param entity: The entity itself to parse.
            :type content_type: string
            :param content_type: The MIME type of the resource.
            :rtype: object
        """
        return None

class EntityWriter(object):
    """ An ``EntityWriter`` is used to write a Python object into a
        serialized form for the HTTP request.
    """
    def is_writable(self, object, content_type):
        """ is_writable(object, content_type) -> boolean
            Return whether this writer can write the specified object
            serialized according to the MIME content type.

            :type content_type: string
            :param content_type: The MIME type of the resource.
            :rtype: Boolean
        """
        return False

    def write(self, object, content_type, to_file):
        """ write(object, content_type, to_file) -> file
            Write the object to the file-like object according to 
            the specified MIME content type.

            :type object: object
            :param object: The Python object to serialize.
            :type content_type: string
            :param content_type: The MIME type of the resource.
            :type to_file: object
            :param to_file: The File object to write the serialized form into.
        """
        return to_file

class JsonReader(EntityReader):
    """ Parse responses from ``application/json`` into Python objects. """
    def is_readable(self, content_type):
        if content_type.find(';') >= 0:
            content_type = content_type[:content_type.find(';')]
        return not json is None and content_type.endswith('/json')

    def read(self, raw_entity, content_type):
        if raw_entity is None or raw_entity.strip() == '':
            return None
        logger.debug('Parsing input as JSON')
        return json.loads(raw_entity)


class JsonWriter(EntityWriter):
    """ Write Python objects into ``application/json``. """
    def is_writable(self, object, content_type):
        if content_type.find(';') >= 0:
            content_type = content_type[:content_type.find(';')]
        return not json is None and content_type.endswith('/json')

    def write(self, object, content_type, to_file):
        json.dump(object, to_file)
        return to_file

class XmlReader(EntityReader):
    """ Parse responses from ``application/xml`` into Python objects. """
    def is_readable(self, content_type):
        if content_type.find(';') >= 0:
            content_type = content_type[:content_type.find(';')]
        if content_type.endswith('/xml') or content_type.endswith('+xml'):
            return True
        return False

    def read(self, raw_entity, content_type):
        if raw_entity is None:
            return None
        logger.debug('Parsing input as XML')
        return fromstring(raw_entity)


class XmlWriter(EntityWriter):
    """ Write Python objects into ``application/xml``. """
    def is_writable(self, object, content_type):
        if content_type.find(';') >= 0:
            content_type = content_type[:content_type.find(';')]
        if content_type.endswith('/xml') or content_type.endswith('+xml'):
            if isinstance(object, _ElementInterface) or isinstance(object, ElementTree):
                return True
        return False

    def write(self, object, content_type, to_file):
        if isinstance(object, _ElementInterface):
            tree = ElementTree(object)
            tree.write(to_file, encoding='utf-8')
        else:
            object.write(to_file, encoding='utf-8')
        return to_file
