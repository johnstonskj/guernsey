# Guernsey REST Client

This is a REST service client library for Python, it is based on the [Jersey client](http://jersey.java.net/nonav/documentation/latest/user-guide.html#client-api) for Java.

Copyright (c) 2011-2015 Simon Johnston (johnstonskj@gmail.com)
<https://github.com/johnstonskj/guernsey>

# Installation

To install simply use setuptools. Note this will install the library as well as the 'resh' REST Shell script.

```zsh
  $ python setup.py install
```

# Generating Documentation

To generate the API documentation simply ensure you have installed [Sphinx](http://sphinx-doc.org/).

```zsh
  $ easy_install -U Sphinx
```

Now, you can use setuptools to build your documentation.

```zsh
  $ python setup.py build_sphinx
```

Documentation is generated, by default, into the `build/sphinx/html` folder.

# Contributing

To get access to the source, you can simply clone the hosted Git repository, as shown below.

```zsh
  $ git clone https://github.com/johnstonskj/guernsey.git
```

You can also run all the test cases (and yes, I need more) from setuptools also.

```zsh
  $ python setup.py test
```
