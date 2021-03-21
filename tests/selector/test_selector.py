import unittest

from pyxmlmapper.components.common import Default
from pyxmlmapper.components.selector import Selector


class TestSelector(unittest.TestCase):
    def setUp(self) -> None:
        self.iterable = [0, 1, 2]

    def test_should_return_first_element(self):
        self.assertEqual(0, Selector(self.iterable).first())

    def test_should_return_last_element(self):
        self.assertEqual(2, Selector(self.iterable).last())

    def test_should_return_by_index(self):
        self.assertEqual(1, Selector(self.iterable).item(1))

    def test_should_support_index_below_zero(self):
        self.assertEqual(0, Selector(self.iterable).item(-3))

    def test_should_return_default_when_index_higher(self):
        self.assertEqual(Default(5), Selector(self.iterable, 5).item(5))

    def test_should_return_default_when_index_lower(self):
        self.assertEqual(Default(5), Selector(self.iterable, 5).item(-5))

    def test_should_support_indexing(self):
        self.assertEqual(0, Selector(self.iterable)[0])
        self.assertEqual(1, Selector(self.iterable)[1])
        self.assertEqual(2, Selector(self.iterable)[2])
        self.assertEqual(2, Selector(self.iterable)[-1])

    def test_should_support_iteration(self):
        self.assertSequenceEqual(self.iterable, list(Selector(self.iterable)))
        self.assertSequenceEqual(self.iterable, Selector(self.iterable).all())


if __name__ == '__main__':
    unittest.main()
