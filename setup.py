from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='pyxmlmapper',
    version='0.0.1',
    packages=find_packages(),
    url='',
    license='',
    author='redlex',
    author_email='sign.rx@ya.ru',
    description='Declarative xml mapping library',
    install_requires=['lxml', 'python-dateutil'],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    scripts=['pyxmlmapper/xml2class.py', 'pyxmlmapper/xml2class_bulk.py']
)
