import unittest
from datetime import datetime

from pyxmlmapper.components.fields import DateTimeField


class TestDateTimeField(unittest.TestCase):
    def test_should_convert_date(self):
        field = DateTimeField("", dayfirst=True)
        date = "01-02-2021"
        self.assertEqual(field.convert_date(date, None), datetime(2021, 2, 1))

        field = DateTimeField("")
        self.assertEqual(field.convert_date(date, None), datetime(2021, 1, 2))

    def test_should_return_default_value_on_error(self):
        field = DateTimeField("", fuzzy=False)
        field._owner_name = "owner"
        field._attr_name = "attr"
        date = "1err"
        self.assertEqual(datetime(1970, 2, 1), field.convert_date(date, datetime(1970, 2, 1)))


if __name__ == '__main__':
    unittest.main()
