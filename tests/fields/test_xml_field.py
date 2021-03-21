import unittest
from lxml import etree
from lxml.etree import XPathSyntaxError

from pyxmlmapper import base
from pyxmlmapper.components.exceptions import NotFoundException
from pyxmlmapper.components.fields import XmlField

xml = """
<PurchaseOrder PurchaseOrderNumber="99503" OrderDate="1999-10-20" EmptyDate="">  
  <Address Type="Shipping">  
    <Name>Ellen Adams</Name>  
    <Street>123 Maple Street</Street>  
    <City>Mill Valley</City>  
    <State>CA</State>  
    <Zip>10999</Zip>  
    <Country>USA</Country>  
  </Address>  
  <Address Type="Billing">  
    <Name>Tai Yee</Name>  
    <Street>8 Oak Avenue</Street>  
    <City>Old Town</City>  
    <State>PA</State>  
    <Zip>95819</Zip>  
    <Country>USA</Country>  
  </Address>  
  <DeliveryNotes>Please leave packages in shed by driveway.</DeliveryNotes>  
  <Items>  
    <Item PartNumber="872-AA">  
      <ProductName>Lawnmower</ProductName>  
      <Quantity>1</Quantity>  
      <USPrice>148.95</USPrice>  
      <Comment>Confirm this is electric</Comment>  
    </Item>  
    <Item PartNumber="926-AA">  
      <ProductName>Baby Monitor</ProductName>  
      <Quantity>2</Quantity>  
      <USPrice>39.98</USPrice>  
      <ShipDate>1999-05-21</ShipDate>  
    </Item>  
  </Items>  
</PurchaseOrder>
"""


class TestXmlFieldExecQuery(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = etree.fromstring(xml)
        XmlField._namespaces = {"auto": True}

    def test_should_return_one_element(self):
        expression = "//Address[1]/Name"
        field = XmlField(expression)
        find = etree.XPath(expression)
        self.assertEqual(1, len(field.exec_query(self.doc)))
        self.assertEqual(find(self.doc), field.exec_query(self.doc))

    def test_should_return_all_elements(self):
        expression = "//Address"
        field = XmlField(expression)
        self.assertEqual(2, len(field.exec_query(self.doc)))

    def test_should_return_empty_list_when_nothing_found(self):
        expression = "//Home/Name"
        field = XmlField(expression)
        find = etree.XPath(expression)
        self.assertEqual(0, len(field.exec_query(self.doc)))
        self.assertEqual(find(self.doc), field.exec_query(self.doc))

    def test_should_throw_if_strict_when_nothing_found(self):
        expression = "//does_not_exists"
        field = XmlField(expression, strict=True)
        self.assertRaises(NotFoundException, lambda: field.exec_query(self.doc))

    def test_should_throw_if_incorrect_expression(self):
        expression = "///incorrect_expression["
        field = XmlField(expression)
        self.assertRaises(XPathSyntaxError, lambda: field.exec_query(self.doc))


class TestXmlFieldValue(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = etree.fromstring(xml)
        XmlField._namespaces = {"auto": True}

    def test_should_return_value(self):
        expression = "//Address[1]/Name"
        field = XmlField(expression)
        self.assertEqual("Ellen Adams", field.value(self.doc))

    def test_should_return_default_if_absent(self):
        expression = "//does_not_exists"
        field = XmlField(expression, default="default value")
        self.assertEqual("default value", field.value(self.doc))

    def test_should_throw_if_strict_when_nothing_found(self):
        expression = "//does_not_exists"
        field = XmlField(expression, strict=True)
        self.assertRaises(NotFoundException, lambda: field.value(self.doc))

    def test_should_return_first_of_found(self):
        expression = "//Address/Name"
        field = XmlField(expression)
        found = etree.XPath(expression)(self.doc)
        self.assertEqual(2, len(found))
        self.assertEqual(found[0].text, field.value(self.doc))


class TestXmlFieldListValue(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = etree.fromstring(xml)
        XmlField._namespaces = {"auto": True}

    def test_should_return_list_of_values(self):
        expression = "//Address/Name"
        field = XmlField(expression)
        self.assertListEqual(["Ellen Adams", "Tai Yee"], field.values_list(self.doc).all())

    def test_should_return_default_if_absent(self):
        expression = "//does_not_exists"
        field = XmlField(expression, default=[])
        self.assertListEqual([], field.values_list(self.doc).all())

    def test_should_throw_if_strict_when_nothing_found(self):
        expression = "//does_not_exists"
        field = XmlField(expression, strict=True)
        self.assertRaises(NotFoundException, lambda: field.values_list(self.doc))


class TestXmlFieldObject(unittest.TestCase):
    class Address(base.BaseXmlParser):
        name = base.ValueField("Name")
        street = base.ValueField("Street")
        city = base.ValueField("City")

    def setUp(self) -> None:
        self.doc = etree.fromstring(xml)
        XmlField._namespaces = {"auto": True}

    def test_should_return_object(self):
        expression = "//Address[1]"
        field = XmlField(expression, pytype=TestXmlFieldObject.Address)
        address = field.object(self.doc)
        self.assertEqual("Ellen Adams", address.name)
        self.assertEqual("Mill Valley", address.city)
        self.assertEqual("123 Maple Street", address.street)

    def test_should_return_default_if_absent(self):
        expression = "//does_not_exists"
        default = TestXmlFieldObject.Address()
        field = XmlField(expression, pytype=TestXmlFieldObject.Address, default=default)
        self.assertIsInstance(field.object(self.doc), TestXmlFieldObject.Address)

    def test_should_throw_if_strict_when_nothing_found(self):
        expression = "//does_not_exists"
        field = XmlField(expression, strict=True)
        self.assertRaises(NotFoundException, lambda: field.object(self.doc))

    def test_should_return_first_of_found(self):
        expression = "//Address"
        field = XmlField(expression, pytype=TestXmlFieldObject.Address)
        found = etree.XPath("//Address/Name")(self.doc)
        self.assertEqual(2, len(found))
        self.assertEqual(found[0].text, field.object(self.doc).name)


if __name__ == '__main__':
    unittest.main()
