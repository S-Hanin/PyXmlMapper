# -*- coding: utf8 -*-

import unittest
from datetime import datetime

from .. import base

xml = """
<PurchaseOrder PurchaseOrderNumber="99503" OrderDate="1999-10-20">  
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


class ItemXmlParser(base.BaseXmlParser):
    product_name = base.ValueField("ProductName")
    part_number = base.ValueField("@PartNumber")
    quantity = base.ValueField("Quantity", pytype=int)
    us_price = base.ValueField("USPrice", pytype=float)


class AddressXmlParser(base.BaseXmlParser):
    name = base.ValueField("Name")
    city = base.ValueField("City")


class PurchaseOrderXmlParser(base.BaseXmlParser):
    order_date = base.DateTimeField('@OrderDate', date_format="%Y-%m-%d")
    address_shipping = base.ObjectField("Address[@Type='Shipping']", AddressXmlParser)
    address_billing = base.ObjectField("Address[@Type='Billing']", AddressXmlParser)
    delivery_notes = base.ValueField("DeliveryNotes")
    items = base.ListObjectField("Items/Item", ItemXmlParser)


class PurchaseItemsXmlParser(base.BaseXmlParser):
    prices = base.ListValueField(".//USPrice")
    typed_prices = base.ListValueField(".//USPrice", pytype=float)
    cities = base.ListValueField(".//City")
    order_types = base.ListValueField(".//@Type")


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
        self.assertEqual(self.obj.address_shipping.name, 'Ellen Adams')
        self.assertEqual(self.obj.address_billing.city, 'Old Town')
        self.assertEqual(self.obj.delivery_notes, 'Please leave packages in shed by driveway.')
        self.assertEqual(self.obj.order_date, datetime(1999, 10, 20))

    def test_list_object_fields_fill(self):
        self.assertEqual(self.obj.items[0].product_name, 'Lawnmower')
        self.assertEqual(self.obj.items.first().product_name, 'Lawnmower')
        self.assertEqual(self.obj.items.last().product_name, 'Baby Monitor')
        self.assertEqual(self.obj.items.last().quantity, 2)
        self.assertEqual(self.obj.items.last().us_price, 39.98)
        self.assertEqual(len(self.obj.items), 2)


class TextXmlParserListFields(unittest.TestCase):
    def setUp(self):
        self.obj = PurchaseItemsXmlParser(xml)

    def test_list_text_fields_fill(self):
        self.assertEqual(self.obj.prices.all(), ['148.95', '39.98'])
        self.assertEqual(self.obj.cities.first(), 'Mill Valley')
        self.assertEqual(self.obj.cities.last(), 'Old Town')
        self.assertEqual(self.obj.order_types.all(), ['Shipping', 'Billing'])

    def test_typed_list_text_fields_fill(self):
        self.assertEqual(self.obj.typed_prices.all(), [148.95, 39.98])


class TestXmlParserNotFoundCases(unittest.TestCase):

    def setUp(self):
        self.obj = PurchaseOrderXmlParser()
        self.obj.set_document(xml)
