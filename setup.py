""" 
The setup/config script for the Guernsey REST client package.
"""

from setuptools import setup, find_packages

import guernsey

setup(name='Guernsey REST Client',
      version='0.1.1',
      description='Guernsey REST Client for Python, based on the Java Jersey API.',
      author='Simon Johnston',
      author_email='simon@johnstonshome.org',
      packages=find_packages(exclude=['test']),
      test_suite='test.suite'
      )
