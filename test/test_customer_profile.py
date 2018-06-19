from content.fixtures.fixtures import PracticeAndRelatedInstances
import datetime
from django.test import TestCase
from payment_authorizenet.customer_profile import CustomerProfile
from payment_authorizenet.enums import (
    AccountType,
    CustomerType,
    ValidationMode)
import time


class TestAuthorizeNetCustomerProfile(TestCase):
    """Test methods of the class CustomerProfile"""

    SUCCESS = 200
    REDIRECT = 301
    FOUND = 302
    NOT_FOUND = 404

    @classmethod
    def setUpTestData(cls):
        cls.ps = PracticeAndRelatedInstances()
        cls.customer_profile = CustomerProfile(cls.ps.practice)

    def test_customer_profile(self):
        """All test of the CustomerProfile methods must be done in
        one function because the tests must be run in order"""

        cp = CustomerProfile(self.ps.practice)

        # the model instance attached to the CustomerProfile
        self.assertTrue(hasattr(cp, 'instance'))

        # Create a CustomerProfile on Authorize.net
        self.assertTrue(
            cp.create_customer_profile('test@test.com'))

        # The customer ID correctly saved on the model
        self.assertTrue(
            cp.instance.authorizenet_customer_profile_id is not None)

        # fake data to use

        dummy_credit_card = '4111111111111111'
        next_year = str(datetime.datetime.now().year + 1)
        expiration_date = '{}-12'.format(next_year)

        # a credit card payment profile

        credit_card_profile = cp.create_customer_payment_profile_credit_card(
            dummy_credit_card,
            expiration_date,
            '123',
            CustomerType.business,
            'Shaun',
            'Overton',
            {},
            'Acme Brick Co',
            True,
            True,  # set as the default payment method
            ValidationMode.liveMode)

        # any valid profile number is > 0, which evaluates to true as a bool
        self.assertTrue(credit_card_profile)

        # the payment profile id should be saved on the model
        self.assertEqual(
            credit_card_profile,
            cp.instance.authorizenet_default_payment_profile_id)

        # create an eCheck payment profile

        contact_dictionary = {
            'address': '123 Sesame St',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10005',
            'country': 'US',
            'phone': '123456789'
        }

        bank_account_profile = cp.create_customer_payment_profile_echeck(
            AccountType.businessChecking,
            '114000093',
            '123456789',
            'Acme Brick Co',
            'Frost Bank',
            CustomerType.business,
            'Shaun',
            'Overton',
            contact_dictionary,
            'Acme Brick Co',
            False,
            False,
            ValidationMode.liveMode)

        # any valid profile number is > 0, which evaluates to true as a bool
        self.assertTrue(bank_account_profile)

        # load CustomerProfile directly from Authorize.net
        cp.get_customer_profile()

        self.assertTrue(hasattr(cp, 'payment_profiles'))
        assert isinstance(cp.payment_profiles, list)

        # update the credit card by changing the CV2 code
        updated_credit_card = cp.update_customer_payment_profile_credit_card(
            str(credit_card_profile),
            dummy_credit_card,
            expiration_date,
            '321',
            CustomerType.business,
            'Shaun',
            'Overton',
            contact_dictionary,
            'Acme Brick Co',
            True,
            True,  # set as the default payment method
            ValidationMode.liveMode)

        # any valid profile number is > 0, which evaluates to true as a bool
        self.assertTrue(updated_credit_card)

        # update the bank account by chnaging the bank name
        updated_bank_account = cp.update_customer_payment_profile_echeck(
            str(bank_account_profile),
            AccountType.businessChecking,
            '114000093',
            '123456789',
            'Acme Brick Co',
            'JP Morgan Chase',
            CustomerType.business,
            'Shaun',
            'Overton',
            contact_dictionary,
            'Acme Brick Co',
            False,
            False,
            ValidationMode.testMode)

        # any valid profile number is > 0, which evaluates to true as a bool
        self.assertTrue(updated_bank_account)

        transaction = cp.charge_customer_profile(
            str(updated_bank_account), '999.99', 'ref id here')

        print('result is', transaction.result)
        print('result == OK?', transaction.result == transaction.OK)

        # self.assertEqual(transaction.result, transaction.OK)

        transaction = cp.charge_customer_profile(
            str(updated_credit_card), '999.99', 'ref id here')

        # self.assertEqual(transaction.result, transaction.OK)

        # delete the echeck payment profile
        self.assertTrue(
            cp.delete_customer_payment_profile(str(updated_bank_account)))

        self.assertTrue(self.customer_profile.delete_customer_profile())


"""
from content.models.practices import Practice
p = Practice.objects.get(pk=14)
from payment_authorizenet.customer_profile import CustomerProfile
cp = CustomerProfile(p)
transaction = cp.charge_customer_profile('1504006837', '3050.50', 'Shell transaction')
transaction.transaction_response.response_code
transaction.approval_code

transaction.transaction_response.response_code == int(transaction.approval_code)
"""
