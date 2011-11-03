#
# Guernsey REST client package, based on the Java Jersey client.
# Copyright (c) 2011 Simon Johnston (simon@johnstonshome.org)
# See LICENSE.txt included in this distribution or more details.
#

from setuptools import setup, find_packages

import guernsey

setup(name='GuernseyRestClient',
      version='0.2.1',
      description='Guernsey REST Client for Python, based on the Java Jersey API.',
      author='Simon Johnston',
      author_email='simon@johnstonshome.org',
      packages=find_packages(exclude=['test']),
      scripts = ['scripts/resh'],
      test_suite='test.suite'
      )
