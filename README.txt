Guernsey REST Client
====================

Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
http://code.google.com/p/guernsey/

Installation
------------

To install simply use setuptools.

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
