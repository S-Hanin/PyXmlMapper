import unittest
from concurrent.futures.thread import ThreadPoolExecutor

from pyxmlmapper import base

xml1 = """
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
</aw:PurchaseOrder>
"""

xml2 = """
<aw:PurchaseOrder  
    aw:PurchaseOrderNumber="99503"  
    aw:OrderDate="1999-10-20"  
    xmlns:aw="http://www.adventure-works.com">  
  <aw:Address aw:Type="Billing">  
    <aw:Name>Tai Yee</aw:Name>  
    <aw:Street>8 Oak Avenue</aw:Street>  
    <aw:City>Old Town</aw:City>  
    <aw:State>PA</aw:State>  
    <aw:Zip>95819</aw:Zip>  
    <aw:Country>USA</aw:Country>  
  </aw:Address>
</aw:PurchaseOrder>
"""


class Address(base.BaseXmlParser):
    name = base.ValueField(".//aw:Name")
    city = base.ValueField(".//aw:City")


class PurchaseOrder(base.BaseXmlParser):
    address_shipping = base.ObjectField(".//aw:Address", Address)


class TestMultithreading(unittest.TestCase):
    def test_each_thread_parses_own_xml(self):
        def parse_name(xml): return PurchaseOrder(xml).address_shipping.name

        with ThreadPoolExecutor(50) as executor:
            for _ in range(1000):
                f1 = executor.submit(parse_name, xml1)
                f2 = executor.submit(parse_name, xml2)
                self.assertEqual(f1.result(), "Ellen Adams")
                self.assertEqual(f2.result(), "Tai Yee")


if __name__ == '__main__':
    unittest.main()
