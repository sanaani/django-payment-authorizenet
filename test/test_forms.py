import datetime
from django.core.validators import MinValueValidator
from django.db import models
from django.test import TestCase
from payment_authorizenet.customer_profile import CustomerProfile
from payment_authorizenet.enums import (
    AccountType,
    CustomerType)
from payment_authorizenet.forms import (
    CreditCardForm,
    ECheckForm)


class TestForms(TestCase):
    """Test the form classes contained in forms.py"""

    @classmethod
    def setUpTestData(cls):
        class FakeModel(models.Model):
            """Create a fake model for use in testing"""
            authorizenet_customer_profile_id = models.IntegerField(
                validators=[MinValueValidator(0)], null=True)
            authorizenet_default_payment_profile_id = models.IntegerField(
                validators=[MinValueValidator(0)], null=True)

        cls.fake_model = FakeModel()

    def get_all_fields_from_form(instance):
        """"
        Return names of all available fields from given Form instance.

        :arg instance: Form instance
        :returns list of field names
        :rtype: list
        """

        fields = []
        for item in instance.__dict__.items():
            if item[0] == 'declared_fields' or item[0] == 'base_fields':
                for field in item[1]:
                    if hasattr(instance.Meta, 'exclude'):
                        if field not in instance.Meta.exclude:
                            fields.append(field)
                    else:
                        fields.append(field)
        return fields

    def test_CreditCardForm(self):
        """CreditCardForm"""

        form = CreditCardForm()

        # confirm that the fields have been sorted by __init__
        self.assertNotEqual(
            TestForms.get_all_fields_from_form(form),
            form.final_key_order[0])

        # Test create_payment_profile
        data = {
            'credit_card_number': '4111111111111111',
            'expiration_month': '12',
            'expiration_year': str(datetime.datetime.now().year + 1),
            'card_code': '123',
            'customer_type': CustomerType.business.name,
            'first_name': 'Shaun',
            'last_name': 'Overton',
            'company_name': 'OneStepRemoved.com, Inc',
            'address': '123 Sesame St',
            'city': 'Hurst',
            'state': 'TX',
            'zip_code': '76054',
            'country': 'US',
            'phone_number': '8171234567',
            'default_method': True
        }

        form = CreditCardForm(data=data)

        # create_payment_profile won't run until the form validates
        with self.assertRaises(ValueError):
            cp = CustomerProfile(self.fake_model)
            form.create_payment_profile(cp)

        self.assertTrue(form.is_valid())

    def test_ECheckForm(self):
        """ECheckForm"""

        form = ECheckForm()

        # confirm that the fields have been sorted by __init__
        self.assertNotEqual(
            TestForms.get_all_fields_from_form(form),
            form.final_key_order[0])

        data = {
            'account_type': AccountType.businessChecking.name,
            'routing_number': '114000093',
            'account_number': '123456789',
            'name_on_account': 'Evexias',
            'bank_name': 'Frost Bank',
            'customer_type': CustomerType.business.name,
            'first_name': 'Shaun',
            'last_name': 'Overton',
            'company_name': 'OneStepRemoved.com, Inc',
            'address': '123 Sesame St',
            'city': 'Hurst',
            'state': 'TX',
            'zip_code': '76054',
            'country': 'US',
            'phone_number': '8171234567',
            'default_method': True
        }

        form = ECheckForm(data=data)

        # create_payment_profile won't run until the form validates
        with self.assertRaises(ValueError):
            cp = CustomerProfile(self.fake_model)
            form.create_payment_profile(cp)

        self.assertTrue(form.is_valid())
