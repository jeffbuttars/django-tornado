#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages


setup(name='django-tornado',
      version='1.1.2',
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
