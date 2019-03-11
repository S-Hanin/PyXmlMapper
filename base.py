# -*- coding: utf8 -*-
import logging
from datetime import datetime
from lxml import etree


# region lxml custom functions


ns = etree.FunctionNamespace(None)


@ns
def lower(context, a):
    """lower-case() function for XPath 1.0"""
    return a.lower()


@ns
def tag(context):
    """:return str
    Returns tag without namespace. Just short replacement for xpath local-name() function
    without arguments"""
    ns_key = context.context_node.prefix
    ns_link = "{{{}}}".format(context.context_node.nsmap.get(ns_key))
    return context.context_node.tag.replace(ns_link, "")


@ns
def match(context, tag, *search):
    """:return bool
    search exact match for tag from several variants
    """
    return any(pattern == tag for pattern in search)


# endregion


class Default:
    def __init__(self, default=None):
        self.default = default

    def __getattr__(self, item):
        return None

    def __bool__(self):
        return False


class Selector:
    def __init__(self, items, default=""):
        self.default = default
        self.items = items

    def first(self):
        if not len(self.items): return Default(self.default)
        return self.items[0]

    def last(self):
        if not len(self.items): return Default(self.default)
        return self.items[-1]

    def item(self, index):
        if len(self.items) < index: return Default(self.default)
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        return self.items[item]

    def __iter__(self):
        for item in self.items:
            yield item


class FieldMeta(type):
    def __call__(cls, *args, **kwargs):
        """set all __init__ arguments to object"""
        obj = type.__call__(cls, *args)
        [setattr(obj, name, kwargs[name]) for name in kwargs]
        return obj


class XmlField(metaclass=FieldMeta):
    def __init__(self, query, parser=None, default=""):

        self._query = query
        self._default = default
        self._parser = parser

    def exec_query(self, doc):
        self._set_doc_namespaces(doc)
        find = etree.XPath(self._query, namespaces=self._namespaces)
        return find(doc)

    def attr(self, doc):
        result = Selector(self.exec_query(doc), self._default)
        return result.first()

    def text(self, doc):
        result = Selector(self.exec_query(doc), self._default)
        try:
            return result.first().text
        except Exception as err:
            logging.debug("{}\n{}".format(err, self._to_string(doc)))

    def object(self, doc):
        result = Selector(self.exec_query(doc), self._default)
        if len(result) > 0:
            return self._parser(result.first())
        else:
            return None

    def list(self, doc):
        result = []
        query_result = self.exec_query(doc)
        for item in query_result:
            result.append(self._parser(item))
        return Selector(result, self._default)

    def _set_doc_namespaces(self, doc):
        if self._namespaces.get('auto'):
            self._namespaces = doc.nsmap
            if None in self._namespaces:
                ns = self._namespaces.pop(None)
                self._namespaces['ns'] = ns

    def _to_string(self, doc):
        return etree.tostring(doc, pretty_print=True)

    def __set_name__(self, owner, name):
        self._attr_name = name
        self._namespaces = getattr(owner, '__namespaces__')


class AttributeField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.attr(instance.document)


class ValueField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.text(instance.document) or ""


class DateTimeField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.convert_date(self.text(instance.document))

    def convert_date(self, date):
        date_format = self.date_format if hasattr(self, 'date_format') else "%Y-%m-%dT%H:%M:%S%z"
        result = datetime.strptime(date, date_format)
        return result


class ObjectField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.object(instance.document)


class ListField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.list(instance.document)


class ParserMeta(type):

    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, *kwargs)

        if not hasattr(obj, "__xml_tree__"):
            obj.__dict__["__xml_tree__"] = None
        return obj


class BaseXmlParser(metaclass=ParserMeta):
    __namespaces__ = {"auto": True}

    def __init__(self, doc=None):
        if doc is not None:
            self.set_document(doc)

    def set_document(self, xml_string):
        if not hasattr(xml_string, 'tag'):
            self.__xml_tree__ = etree.fromstring(xml_string)
        else:
            self.__xml_tree__ = xml_string

    @property
    def document(self):
        return self.__xml_tree__


