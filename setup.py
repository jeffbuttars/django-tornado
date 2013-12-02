#!/usr/bin/env python
# encoding: utf-8

import setuptools
from setuptools import setup, find_packages


setup(name='django-tornado',
4     version='1.1.5',
      description="Django/Tornado integration made easy.",
      author="Jeff Buttars",
      author_email="jeffbuttars@gmail.com",
      packages=find_packages(),
      license='MIT',
      package_dir={'django_tornado': 'django_tornado'},
      install_requires=[
          'tornado',
          'Django',
      ],
      # data_files=[
      #     ('/etc/init.d', ['conf/init.d/afile']),
      # ],
      )
