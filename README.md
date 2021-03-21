# xml_mapper
Declarative xml to object mapper

### requirements
`lxml 4.3`

### installation
```bash
git clone https://github.com/S-Hanin/xml_mapper.git
cd xml_mapper && python setup.py install
```
or just add it to your requirements.txt
```text
git+https://github.com/S-Hanin/xml_mapper.git#egg=pyxmlmapper
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
from pyxmlmapper import base
from pyxmlmapper import fields


class Item(base.BaseXmlParser):
    __namespaces__ = {'aw': 'http://www.adventure-works.com'}

    product_name = fields.ValueField("aw:ProductName")
    part_number = fields.ValueField("@aw:PartNumber")
    quantity = fields.ValueField("aw:Quantity", pytype=int)
    us_price = fields.ValueField("aw:USPrice", pytype=float)


class Address(base.BaseXmlParser):
    name = fields.ValueField("aw:Name")
    city = fields.ValueField("aw:City")


class PurchaseOrder(base.BaseXmlParser):
    order_date = fields.DateTimeField('@aw:OrderDate')
    address_shipping = fields.ObjectField("aw:Address[@aw:Type='Shipping']", Address)
    address_billing = fields.ObjectField("aw:Address[@aw:Type='Billing']", Address)
    delivery_notes = fields.ValueField("aw:DeliveryNotes")
    items = fields.ListObjectField(".//aw:Item", Item)
    

purchase_order = PurchaseOrder(xml) # xml - string or xml tree

print(purchase_order.address_billing.name)
print(purchase_order.delivery_notes)

for item in purchase_order.items:
    print(item.product_name)

```

_Note that namespaces declaration is not necessary_

### fields

Import ways:
```python
from pyxmlmapper import base
from pyxmlmapper.components.fields import *
from pyxmlmapper import fields
```

Field definition:
```python
from pyxmlmapper import fields

xml_field = fields.XmlField(query='', pytype=str, default='', strict=False)
```
`XmlField` is a base for other field types.    
- `query` - XPath query  
- `pytype` - type to convert extracted value to, basically there might be any callable which accepts string and returns some value  
- `default` - default value if nothing found  
- `strict` - boolean. Indicates that xml field is mandatory. If True and nothing found then `NotFoundException` will be raised  

`ValueField` - represents xml node without children. ( Returns the first found if there are more than one field )  
`ListValueField` - represents xml nodes which have the same name and have no children  
`ObjectField` - represents xml node with children. ( Returns the first found if there are more than one field )  
`ListObjectField` - represents xml nodes which have the same name and have children    

`DateTimeField` - special field for datetime values, there is python-dateutil under the hood.  
```python
from pyxmlmapper import fields
from datetime import datetime

date = fields.DateTimeField(query='', default=datetime(2021, 1, 1), dayfirst=False, yearfirst=False, fuzzy=True)
```
- `query` - XPath query  
- `default` - default value to return if xml value can't be parsed  
- `dayfirst` - in the case when date is ambiguous like '01-01-2021'  
- `yearfirst` - in the case when date is ambiguous like '21-01-01'  
- `fuzzy` - allow dateutil fuzzy parsing  

[ read dateutil docs ](https://dateutil.readthedocs.io/en/stable/parser.html)  


To avoid prefix declaration in xpath it's possible to use additional xpath functions:

```python
from pyxmlmapper import fields

product_name = fields.ValueField(".//*[tag()='ProductName']")
product_name = fields.ValueField(".//*[match(tag(), 'ProductName')]")
product_name = fields.ValueField(".//*[match(tag(), 'ProductName', 'product_name')]") # if tag name is not permanent
```

or you can add your own xpath functions

```python
from pyxmlmapper import xpath_functions

@xpath_functions.ns
def lower(context, a):
    """lower-case() function for XPath 1.0"""
    return a.lower()
```

and use it

```python
from pyxmlmapper import fields

product_name = fields.ValueField(".//*[lower(tag())='productname']")
```

more about xpath functions:
https://lxml.de/extensions.html#xpath-extension-functions