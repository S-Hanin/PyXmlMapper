# -*- coding: utf8 -*-
import logging
import dateutil
from lxml import etree

logger = logging.getLogger('PyXmlMapper')


class NotFoundExcetion(Exception):
    pass


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
        return self.default

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

    def all(self):
        return self.items

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
        [setattr(obj, "_" + name, kwargs[name]) for name in kwargs]
        return obj


class TypeCastMixin:
    def convert(self, _type, value):
        try:
            if isinstance(value, Default): return value.default
            return _type(value)
        except Exception as err:
            logger.critical(err)
            raise TypeError(err)


class XmlField(TypeCastMixin, metaclass=FieldMeta):
    def __init__(self, query, pytype=str, default="", strict=False):

        self._query = query
        self._default = default
        self._pytype = pytype
        self._strict = strict

    def exec_query(self, doc):
        self._set_doc_namespaces(doc)
        find = etree.XPath(self._query, namespaces=self._namespaces)
        result = [] if not doc else find(doc)
        if len(result) == 0 and self._strict:
            raise NotFoundExcetion
        return result

    def value(self, doc):
        result = Selector(self.exec_query(doc), self._default)
        try:
            return self.convert(self._pytype, getattr(result.first(), 'text', result.first()))
        except Exception as err:
            logger.debug("{}\n{}".format(err, self._to_string(doc)))
            raise

    def values_list(self, doc):
        query_result = self.exec_query(doc)
        result = [self.convert(self._pytype, getattr(item, 'text', item)) for item in query_result]
        return Selector(result, self._default)

    def object(self, doc):
        result = Selector(self.exec_query(doc), self._default)
        return self.convert(self._pytype, result.first())

    def objects_list(self, doc):
        result = []
        query_result = self.exec_query(doc)
        for item in query_result:
            result.append(self.convert(self._pytype, item))
        return Selector(result, self._default)

    def _set_doc_namespaces(self, doc):
        if not doc:
            self._namespaces = {}
            return
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


class ValueField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.value(instance.document)


class ListValueField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.values_list(instance.document)


class DateTimeField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        self._owner_name = instance.__class__.__name__
        return self.convert_date(self.value(instance.document), self._default)

    def convert_date(self, date, default):
        try:
            return dateutil.parser.parse(date)
        except ValueError as err:
            logger.warning("{{ '{}':: Attr: '{}', Query: '{}' }} Exception: {}"
                           .format(self._owner_name, self._attr_name, self._query, err))
        except OverflowError as err:
            logger.warning("{{ '{}':: Attr: '{}', Query: '{}' }} Exception: {}"
                           .format(self._owner_name, self._attr_name, self._query, err))

        if default:
            result = dateutil.parser.parse(self._default)
        else:
            raise ValueError("Can't convert value {} to date. {{ '{}':: Attr: '{}', Query: '{}' }}"
                             .format(date, self._owner_name, self._attr_name, self._query))

        return result


class ObjectField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.object(instance.document)


class ListObjectField(XmlField):

    def __get__(self, instance, owner):
        if not instance: return self
        return self.objects_list(instance.document)


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
    def raw_xml(self):
        return etree.tostring(self.document, encoding="utf8", pretty_print=True)

    @property
    def document(self):
        return self.__xml_tree__
