from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='PyXmlMapper',
    version='0.0.1',
    packages=find_packages(),
    url='',
    license='',
    author='redlex',
    author_email='domini.lex@gmail.com',
    description='Declarative xml mapping library', install_requires=['lxml', 'python-dateutil'],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    scripts=['xml2class.py', 'xml2class_bulk.py']
)
