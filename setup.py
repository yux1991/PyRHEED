import sys
import subprocess
from setuptools import setup, find_packages

with open('requirements.txt', encoding='UTF-8') as f:
    required = f.read().splitlines()

setup(
   name='PyRHEED',
   python_requires=">=3.12",
   version='1.0',
   description='A python program for RHEED data analysis', 
   author='Yu Xiang',
   author_email='yux1991@gmail.com',
   install_requires=required,
)
