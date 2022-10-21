import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
   name='PyRHEED',
   version='1.0',
   description='A python program for RHEED data analysis', 
   author='Yu Xiang',
   author_email='yux1991@gmail.com',
   packages=find_packages(),
   install_requires=required
)
