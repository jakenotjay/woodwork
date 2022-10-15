#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='woodwork',
      version='0.0.1',
      description='Package containing core functionality to producing segmentation of forest loss.',
      author='Jake Wilkins',
      author_email='jwilkins0519@gmail.com',
      url='',
      install_requires=["google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib", "earthengine-api"],
      packages=find_packages(include=["woodwork", "woodwork.*"]),
      package_data={"woodwork": ["data/*.json"]},
      classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: GIS",
            "Development Status :: 2 - Pre-Alpha"
      ]
    )