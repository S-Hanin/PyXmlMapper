# -*- coding: utf8 -*-

from .components.xpath_functions import *
from .components.fields import *
from .components.exceptions import *


class BaseXmlParser:
    __namespaces__ = {"auto": True}

    def __init__(self, doc=None):
        self.__xml_tree__ = None
        if doc is not None:
            self.set_document(doc)

    def set_document(self, xml_string):
        if not hasattr(xml_string, 'tag'):
            self.__xml_tree__ = etree.fromstring(xml_string, etree.XMLParser(recover=True))
        else:
            self.__xml_tree__ = xml_string

    @property
    def raw_xml(self):
        return etree.tostring(self.document, encoding="utf8", pretty_print=True)

    @property
    def document(self):
        return self.__xml_tree__
