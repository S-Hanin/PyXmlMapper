# xml_mapper
Declarative xml to object mapper

### requirements
`lxml 4.3`

### installation
```bash
git clone https://github.com/S-Hanin/xml_mapper.git
cd xml_mapper && python setup.py install
```
### usage
xml example
```xml
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
```

define classes for mapping

```python
from PyXmlMapper import base
from PyXmlMapper import fields


class ItemXmlParser(base.BaseXmlParser):
    __namespaces__ = {'aw': 'http://www.adventure-works.com'}

    product_name = fields.ValueField("aw:ProductName")
    part_number = fields.ValueField("@aw:PartNumber")
    quantity = fields.ValueField("aw:Quantity", pytype=int)
    us_price = fields.ValueField("aw:USPrice", pytype=float)


class AddressXmlParser(base.BaseXmlParser):
    name = fields.ValueField("aw:Name")
    city = fields.ValueField("aw:City")


class PurchaseOrderXmlParser(base.BaseXmlParser):
    order_date = fields.DateTimeField('@aw:OrderDate', date_format="%Y-%m-%d")
    address_shipping = fields.ObjectField("aw:Address[@aw:Type='Shipping']", AddressXmlParser)
    address_billing = fields.ObjectField("aw:Address[@aw:Type='Billing']", AddressXmlParser)
    delivery_notes = fields.ValueField("aw:DeliveryNotes")
    items = fields.ListObjectField(".//aw:Item", ItemXmlParser)
    

purchase_order = PurchaseOrderXmlParser(xml) # xml - string or xml tree

print(purchase_order.address_billing.name)
print(purchase_order.delivery_notes)

for item in purchase_order.items:
    print(item.product_name)

```

_Note that namespaces declaration is not necessary_

To avoid prefix declaration in xpath it's possible to use additional xpath functions:
```python
from PyXmlMapper import fields

product_name = fields.ValueField(".//*[tag()='ProductName']")
product_name = fields.ValueField(".//*[match(tag(), 'ProductName')]")
product_name = fields.ValueField(".//*[match(tag(), 'ProductName', 'product_name')]") # if tag name is not permanent
```

or you can add your own xpath functions

```python
from PyXmlMapper import xpath_functions

@xpath_functions.ns
def lower(context, a):
    """lower-case() function for XPath 1.0"""
    return a.lower()
```

and use it

```python
product_name = fields.ValueField(".//*[lower(tag())='productname']")
```

more about xpath functions:
https://lxml.de/extensions.html#xpath-extension-functions