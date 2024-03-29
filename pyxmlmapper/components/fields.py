import logging

from dateutil import parser as date_parser
from lxml import etree

from .exceptions import NotFoundException
from .mixins import TypeCastMixin
from .selector import Selector

logger = logging.getLogger(__name__)


class XmlField(TypeCastMixin):
    def __init__(self, query, pytype=str, default="", strict=False):

        self._query = query
        self._default = default
        self._pytype = pytype
        self._strict = strict

    def __set_name__(self, owner, name):
        self._attr_name = name
        self._namespaces = getattr(owner, '__namespaces__')

    def exec_query(self, doc):
        self._set_doc_namespaces(doc)
        find = etree.XPath(self._query, namespaces=self._namespaces)
        result = [] if doc is None else find(doc)
        if len(result) == 0 and self._strict:
            raise NotFoundException
        return result

    def value(self, doc):
        result = Selector(self.exec_query(doc), self._default)
        return self.convert(self._pytype, getattr(result.first(), 'text', result.first()))

    def object(self, doc):
        result = Selector(self.exec_query(doc), self._default)
        return self.convert(self._pytype, result.first())

    def values_list(self, doc):
        query_result = self.exec_query(doc)
        result = [self.convert(self._pytype, getattr(item, 'text', item)) for item in query_result]
        return Selector(result, self._default)

    def objects_list(self, doc):
        query_result = self.exec_query(doc)
        result = [self.convert(self._pytype, item) for item in query_result]
        return Selector(result, self._default)

    def _set_doc_namespaces(self, doc):
        if doc is None:
            self._namespaces = {}
            return
        if self._namespaces.get('auto'):
            self._namespaces = doc.nsmap
            if None in self._namespaces:
                ns = self._namespaces.pop(None)
                self._namespaces['ns'] = ns

    @staticmethod
    def _to_string(doc):
        return etree.tostring(doc, pretty_print=True)


def __get_decorator(method):
    def get(self, instance, owner):
        call = getattr(self, method)
        return call(instance.document) if instance else self

    def wrap(cls):
        cls.__get__ = get
        return cls

    return wrap


@__get_decorator("value")
class ValueField(XmlField): pass


@__get_decorator("values_list")
class ListValueField(XmlField): pass


@__get_decorator("object")
class ObjectField(XmlField): pass


@__get_decorator("objects_list")
class ListObjectField(XmlField): pass


class DateTimeField(XmlField):
    def __init__(self, *args, dayfirst=False, yearfirst=False, fuzzy=True, **kwargs):
        super().__init__(*args, **kwargs)
        self._parserinfo = date_parser.parserinfo(dayfirst=dayfirst, yearfirst=yearfirst)
        self._fuzzy = fuzzy

    def __get__(self, instance, owner):
        if not instance:
            return self
        self._owner_name = instance.__class__.__name__
        return self.convert_date(self.value(instance.document), self._default)

    def convert_date(self, date, default):
        try:
            return date_parser.parse(date, fuzzy=self._fuzzy, parserinfo=self._parserinfo)
        except (ValueError, OverflowError) as err:
            logger.warning("{{ '{}':: Attr: '{}', Query: '{}' }} Exception: {}"
                           .format(self._owner_name, self._attr_name, self._query, err))

        if default:
            return default
        else:
            raise ValueError("Can't convert value {} to date. {{ '{}':: Attr: '{}', Query: '{}' }}"
                             .format(date, self._owner_name, self._attr_name, self._query))
