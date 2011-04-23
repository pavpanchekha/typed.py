#!/usr/bin/env python

from distutils.core import setup

# If there's one thing the Haskell folks got right, it was code layout
setup( name    = "typed.py"
     , version = "1.0.0.1"
     , author  = "Pavel Panchekha"
     , author_email = "pavpanchekha@gmail.com"
     , url     = "http://pypi.python.org/pypi/typed.py/"
     , license = "LICENSE.txt"
     , packages= ["typed"]
     , description = "Inquisitive types and multiple dispatch, now for Python!"
     , long_description = open("README.rst").read()

     , classifiers = [
           "Development Status :: 4 - Beta"
         , "Intended Audience :: Developers"
         , "License :: OSI Approved :: GNU General Public License (GPL)"
         , "Programming Language :: Python :: 2.6"
         , "Topic :: Software Development :: Libraries :: Python Modules"
         ]
     )



