#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

try:
    import json
except:
    json = None

class EntityReader(object):
    """ An ``EntityReader`` is used to read a raw entity from the
        HTTP response and construct a Python object representation.
    """
    def is_readable(self, content_type):
        """ is_readable(content_type) -> boolean
            Return whether this reader can read an object serialized
            with the specified MIME content type.
        """
        return False

    def read(self, entity, content_type):
        """ read(entity, content_type) -> object
            Read and parse the entity and return an object representation.
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
        """
        return False

    def write(self, object, content_type, to_file):
        """ write(object, content_type, to_file) -> file
            Write the object to the file-like object according to 
            the specified MIME content type.
        """
        return to_file

class JsonReader(EntityReader):
    def is_readable(self, content_type):
        return not json is None and content_type.endswith('json')

    def read(self, raw_entity, content_type):
        return json.loads(raw_entity)


class JsonWriter(EntityWriter):
    def is_writable(self, object, content_type):
        return not json is None and content_type.endswith('json')

    def write(self, object, content_type, to_file):
        json.dump(object, to_file)
        return to_file
