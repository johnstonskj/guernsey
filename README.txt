Guernsey REST Client
====================

This is a REST service client library for Python, it is based on the Jersey client for Java.

See http://jersey.java.net/nonav/documentation/latest/user-guide.html#client-api

Copyright (c) 2011 Simon Johnston (johnstonskj@gmail.com)
http://code.google.com/p/guernsey/

Installation
------------

To install simply use setuptools. Note this will install the 
library as well as the 'resh' REST Shell script.

  $ python setup.py install

Generating Documentation
------------------------

To generate the API documentation simply ensure you have installed
Sphinx:

  $ easy_install -U Sphinx

Now, you can use setuptools to build your documentation.

  $ python setup.py build_sphinx

Documentation is generated, by default, into the build/sphinx/html
folder.

Contributing
------------

To get access to the source, you can simply clone the hosted Git
repository, as shown below.

  $ git clone https://code.google.com/p/guernsey/

You can also run all the test cases (and yes, I need more) from
setuptools also.

  $ python setup.py test

