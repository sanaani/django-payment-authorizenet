from django.test import TestCase
from payment_authorizenet.enums import EnumTuple


class MyEnum(EnumTuple):
    option1 = 'Vanilla'
    option2 = 'Chocolate'
    option3 = 'Strawberry'


class TestEnumTuple(TestCase):
    """Test functions saved in enums.py"""

    def test_as_tuple(self):
        """Test as_tuple, which is intended to be used as choices within
        a model or form field"""

        my_tuple = MyEnum.as_tuple()

        expected_value = (
            ('option1', 'Vanilla'),
            ('option2', 'Chocolate'),
            ('option3', 'Strawberry'))

        self.assertEqual(my_tuple, expected_value)

    def test_as_tuple_with_all(self):
        """Identical to as_tuple, except that the last option contains All"""

        my_tuple = MyEnum.as_tuple_with_all()

        expected_value = (
            ('option1', 'Vanilla'),
            ('option2', 'Chocolate'),
            ('option3', 'Strawberry'),
            ('all', 'All'))

        self.assertEqual(my_tuple, expected_value)

    def test_str_list(self):
        """.str_list() should return all values with commas
        in the appropriate spots"""

        my_str = MyEnum.str_list()
        expected_value = 'Vanilla, Chocolate, Strawberry'

        self.assertEqual(my_str, expected_value)
