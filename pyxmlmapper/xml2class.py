#!python
# -*- coding: utf8 -*-

import logging
from argparse import ArgumentParser
from collections import OrderedDict
from io import StringIO

from dateutil import parser as date_parser
from lxml import etree

import pyxmlmapper.components.xpath_functions

logging.basicConfig(level=logging.INFO)

arg_parser = ArgumentParser(description="Creates classes from xml file. Tool for pyxmlmapper lib")
arg_parser.add_argument("filename", nargs="?", help="path to xml file")


class Node(object):
    def __init__(self, name, value, path, parent, children=None):
        self.name = name
        self.value = value
        self.path = path
        self.relative_path = path.split("/")[-1] if "/" in path else path
        self._parent = parent
        self.children = children or []

    @property
    def parent(self):
        return self._parent

    def add_child(self, node):
        self.children.append(node)

    @property
    def has_children(self):
        return len(self.children) > 0

    def has_same_child(self, node):
        return sum([n.name == node.name for n in self.children]) > 1

    def has_same_siblings(self, node):
        if not self.parent: return False
        return sum([n.name == node.name for n in self.parent.children]) > 1

    def accept(self, visitor):
        visitor.visit(self)

    def iterwalk(self, visitor):
        self.accept(visitor)
        visitor.up()
        for item in self.children:
            item.iterwalk(visitor)
        visitor.down()

    def __repr__(self):
        return self.name


def replace_ns(element):
    ns = "{{{}}}".format(element.nsmap.get(element.prefix, ''))
    prefix = "{}:".format(element.prefix) if element.prefix else ''
    return element.tag.replace(ns, prefix)


def remove_ns(element):
    ns = "{{{}}}".format(element.nsmap.get(element.prefix, ''))
    return element.tag.replace(ns, '')


def replace_ns_in_path(path, nsmap):
    result = path
    for prefix, ns in nsmap.items():
        ns = "{{{}}}".format(ns)
        prefix = "{}:".format(prefix) if prefix else ''
        result = result.replace(ns, prefix)
    return result


def strip(string):
    return string.strip() if string else ''


def upper_first_letter(string):
    return "{}{}".format(string[0].upper(), string[1:]) if string else ''


def build_tree(element_tree):
    current = None
    for event, element in etree.iterwalk(element_tree, events=('start', 'end')):
        if event == "start":
            node = Node(name=remove_ns(element),
                        value=element.text,
                        path=replace_ns_in_path(element_tree.getelementpath(element), element.nsmap),
                        parent=current)
            # if element has no text and it's not a root element then add his child and go deeper
            if not strip(element.text):
                if current is not None:
                    current.add_child(node)
                current = node
            else:
                current.add_child(node)
        if event == "end":  # go upper
            if not strip(element.text):
                current = current.parent if current.parent else current
    return current


class PrintVisitor(object):
    level = 0

    @classmethod
    def up(cls):
        cls.level += 1

    @classmethod
    def down(cls):
        cls.level -= 1

    @classmethod
    def visit(cls, item):
        value = strip(item.value) if item.value else ''
        logging.info("{}{}: {}\t\t./{}".format("\t" * cls.level, item.name, value.encode("utf8"), item.path))

    pass


class CodeBuilder(object):
    def __init__(self):
        self.level = 0
        self.models = OrderedDict()

    def up(self):
        self.level += 1

    def down(self):
        self.level -= 1

    def visit(self, item):
        if item.has_children:
            self.create_model(item)
        else:
            self.create_attribute(item)

    def create_model(self, item):
        class_definition = ["class {}(base.BaseXmlParser):".format(upper_first_letter(item.name))]
        self.models[item.name] = class_definition
        if item.has_same_siblings(item):
            self.add_listobject_field(item)
        else:
            self.add_object_field(item)

    def create_attribute(self, item):
        if item.has_same_siblings(item):
            self.add_listvalue_field(item)
        else:
            self.add_value_field(item)

    def add_value_field(self, item):
        if item.parent is None: return
        class_definition = self.models[item.parent.name]
        # tries to recognize date or datetime value
        try:
            if len(item.value) < 10: raise Exception()  # if value smaller than 10 symbols it's too hard to recognize date value
            date = date_parser.parse(item.value)  # this line throws an exception if date_parser can't recognize value
            attr_definition = ("\t{item.name} = base.DateTimeField('./{item.relative_path}')  # {comment}"
                               .format(item=item, comment=strip(item.value)))
        except:
            attr_definition = ("\t{item.name} = base.ValueField('./{item.relative_path}')  # {comment}"
                               .format(item=item, comment=strip(item.value)))
        class_definition.append(attr_definition)

    def add_object_field(self, item):
        if item.parent is None: return
        class_definition = self.models[item.parent.name]
        attr_definition = ("\t{item.name}: {classname} = base.ObjectField('./{item.relative_path}', {classname}, default={classname}())"
                           .format(item=item, classname=upper_first_letter(item.name)))
        class_definition.append(attr_definition)

    def add_listvalue_field(self, item):
        if item.parent is None: return
        class_definition = self.models[item.parent.name]
        attr_definition = ("\t{item.name}s = base.ListValueField('./{item.relative_path}', default={item.name}())  # {comment}"
                           .format(item=item, comment=strip(item.value)))
        class_definition.append(attr_definition)

    def add_listobject_field(self, item):
        if item.parent is None: return
        class_definition = self.models[item.parent.name]
        attr_definition = ("\t{item.name}s: List[{classname}] = base.ListObjectField('./{item.relative_path}', {classname}, default={classname}())"
                           .format(item=item, classname=upper_first_letter(item.name)))
        for line in class_definition:
            if item.name in line:
                return
        class_definition.append(attr_definition)

    def render_to_string(self):
        result = StringIO()
        result.write("#  -*- coding: utf8 -*-\n\n")
        result.write("from pyxmlmapper import base\n")
        result.write("from typing import List\n\n\n")
        for definition in reversed(self.models.values()):
            result.write("\n".join(definition))
            result.write("\n\n\n")
        return result.getvalue()


def create_classes_from_file(filename):
    xml = etree.parse(filename)
    obj_tree = build_tree(xml)
    builder_visitor = CodeBuilder()
    obj_tree.iterwalk(builder_visitor)
    result = builder_visitor.render_to_string()
    if isinstance(filename, str):
        result = "#  {}\n\n{}".format(filename, result)
    return result


def create_classes_from_string(xml_string):
    xml = etree.fromstring(xml_string)
    obj_tree = build_tree(xml)
    builder_visitor = CodeBuilder()
    obj_tree.iterwalk(builder_visitor)
    result = builder_visitor.render_to_string()
    return result


def main():
    args = arg_parser.parse_args()
    print("#  {}\n\n".format(args.filename))
    xml = etree.parse(args.filename)
    obj_tree = build_tree(xml)
    builder_visitor = CodeBuilder()
    obj_tree.iterwalk(builder_visitor)
    print(builder_visitor.render_to_string())


if __name__ == "__main__":
    main()
