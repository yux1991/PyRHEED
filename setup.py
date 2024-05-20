import sys
import subprocess
from setuptools import setup, find_packages

with open('requirements.txt', encoding='UTF-8') as f:
    required = f.read().splitlines()

subprocess.check_call([sys.executable, "-m", "pip", "install", 'numpy==1.21.6'])
subprocess.check_call([sys.executable, "-m", "pip", "install", 'pyqtdatavisualization==5.15.5'])
subprocess.check_call([sys.executable, "-m", "pip", "install", 'pyQtCharts==5.15.6'])

setup(
   name='PyRHEED',
   python_requires=">=3.7.4",
   version='1.0',
   description='A python program for RHEED data analysis', 
   author='Yu Xiang',
   author_email='yux1991@gmail.com',
   packages=find_packages(),
   install_requires=required,
   extra_require = {"CUDA": ["pycuda==2022.1"]}
)
