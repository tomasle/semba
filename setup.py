# $Id: setup.py 31 2010-01-12 15:44:40Z tlev $
# -*- coding: iso-8859-1 -*-

'''
Created on 30. okt. 2009

@author: levin
'''#!/usr/bin/env python



from distutils.core import setup

setup(name='SEMBA',
      version='1.0',
      description='SINTEF Emission Module Based On ARTEMIS',
      author='Tomas Levin',
      author_email='Tomas.Levin@sintef.no',
      long_description =' This is the toolkit to do transport research with. \n You will need the  \
      following additional packages installed to get all functionality to work. \n NUMPY, SICPY, Matplot', 
      url='http://www.sintef.no',
      packages=['SEMBA']
     )
