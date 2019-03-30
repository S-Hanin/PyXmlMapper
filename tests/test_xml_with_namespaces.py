# -*- coding: utf8 -*-

import unittest

from PyXmlMapper import base

xml = """
<aw:PurchaseOrder  
    aw:PurchaseOrderNumber="99503"  
    aw:OrderDate="1999-10-20"  
    xmlns:aw="http://www.adventure-works.com">  
  <aw:Address aw:Type="Shipping">  
    <aw:Name>Ellen Adams</aw:Name>  
    <aw:Street>123 Maple Street</aw:Street>  
    <aw:City>Mill Valley</aw:City>  
    <aw:State>CA</aw:State>  
    <aw:Zip>10999</aw:Zip>  
    <aw:Country>USA</aw:Country>  
  </aw:Address>  
  <aw:Address aw:Type="Billing">  
    <aw:Name>Tai Yee</aw:Name>  
    <aw:Street>8 Oak Avenue</aw:Street>  
    <aw:City>Old Town</aw:City>  
    <aw:State>PA</aw:State>  
    <aw:Zip>95819</aw:Zip>  
    <aw:Country>USA</aw:Country>  
  </aw:Address>  
  <aw:DeliveryNotes>Please leave packages in shed by driveway.</aw:DeliveryNotes>  
  <aw:Items>  
    <aw:Item aw:PartNumber="872-AA">  
      <aw:ProductName>Lawnmower</aw:ProductName>  
      <aw:Quantity>1</aw:Quantity>  
      <aw:USPrice>148.95</aw:USPrice>  
      <aw:Comment>Confirm this is electric</aw:Comment>  
    </aw:Item>  
    <aw:Item aw:PartNumber="926-AA">  
      <aw:ProductName>Baby Monitor</aw:ProductName>  
      <aw:Quantity>2</aw:Quantity>  
      <aw:USPrice>39.98</aw:USPrice>  
      <aw:ShipDate>1999-05-21</aw:ShipDate>  
    </aw:Item>  
  </aw:Items>  
</aw:PurchaseOrder> 
"""


class ItemXmlParser(base.BaseXmlParser):
    __namespaces__ = {'aw': 'http://www.adventure-works.com'}

    product_name = base.ValueField(".//aw:ProductName")
    part_number = base.ValueField("./@aw:PartNumber")
    quantity = base.ValueField(".//aw:Quantity")
    us_price = base.ValueField(".//aw:USPrice")


class AddressXmlParser(base.BaseXmlParser):
    name = base.ValueField(".//aw:Name")
    city = base.ValueField(".//aw:City")


class PurchaseOrderXmlParser(base.BaseXmlParser):
    address_shipping = base.ObjectField(".//aw:Address[@aw:Type='Shipping']", AddressXmlParser)
    address_billing = base.ObjectField(".//aw:Address[@aw:Type='Billing']", AddressXmlParser)
    delivery_notes = base.ValueField(".//aw:DeliveryNotes")
    items = base.ListObjectField(".//aw:Item", ItemXmlParser)


class TestXmlParserCreation(unittest.TestCase):

    def setUp(self):
        self.obj = PurchaseOrderXmlParser()
        self.obj.set_document(xml)

    def test_parser_create(self):
        self.assertTrue(self.obj)

    def test_parser_has_special_fields(self):
        self.assertTrue(hasattr(self.obj, '__xml_tree__'))

    def test_set_document(self):
        self.assertTrue(self.obj.document)

    def test_value_fields_fill(self):
        self.assertTrue(self.obj.address_shipping.name == 'Ellen Adams')
        self.assertTrue(self.obj.address_billing.city == 'Old Town')
        self.assertTrue(self.obj.delivery_notes == 'Please leave packages in shed by driveway.')

    def test_list_fields_fill(self):
        self.assertTrue(self.obj.items[0].product_name == 'Lawnmower')
        self.assertTrue(self.obj.items.first().product_name == 'Lawnmower')
        self.assertTrue(self.obj.items.first().part_number == '872-AA')
        self.assertTrue(self.obj.items.last().product_name == 'Baby Monitor')
        self.assertTrue(self.obj.items.last().quantity == '2')
        self.assertTrue(self.obj.items.last().us_price == '39.98')


class TestXmlParserNotFoundCases(unittest.TestCase):

    def setUp(self):
        self.obj = PurchaseOrderXmlParser()
        self.obj.set_document(xml)
