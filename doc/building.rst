Building Guernsey
-----------------

To install simply use the standard Python ``setuptools``; while
this would handle dependencies for you it is worth noting that 
Guernsey has no external dependencies beyond the standard 
Python 2.6 library::

  $ python setup.py install

Note this will install the library as well as the ``resh`` REST 
Shell script (see `Google Code Wiki 
<http://code.google.com/p/guernsey/wiki/RestShell>`_ for more
details).

Generating This Documentation
*****************************

To generate the full documentation you must ensure you have first
installed the Sphinx documentation tools::

  $ easy_install -U Sphinx

Now, you can use ``setuptools`` again to build your documentation.::

  $ python setup.py build_sphinx

Documentation is generated, by default, into the ``build/sphinx/html``
folder, the following command on Mac OS X will open the documentation
in a new browser.::

  $ open build/sphinx/html/index.html

Contributing
************

To get access to the source, you can simply clone the hosted Git
repository, as shown below::

  $ git clone https://code.google.com/p/guernsey/

You can also run all the test cases (and yes, I need more) from
``setuptools`` as expected::

  $ python setup.py test

