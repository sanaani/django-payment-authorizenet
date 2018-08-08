import calendar
from collections import OrderedDict
import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from payment_authorizenet import constants
from payment_authorizenet.enums import (
    AccountType,
    CustomerType)
from payment_authorizenet.merchant_auth import AuthorizeNetError


# ****************** Validators

def exact_length(expected_length):
    """Confirm that a string has exactly expected_length chars
    This function exists to faciliate using validation with custom args

    Argument explanation:
        - expected_length - how many chars should there be in a string?
    """

    def validate(value):
        _length = len(value)

        if _length != expected_length:
            raise ValidationError(
                '%(value)s must be exactly %(expected_length)s chars long',
                params={'value': value, 'expected_length': expected_length})

    return validate


def is_integer(value):
    """Confirm that the characters of the string value make a whole number"""

    try:
        int(value)
    except ValueError:
        raise ValidationError(
            _('%(value)s must be a 9 digit integer'),
            params={'value': value},)


def length_range(_min, _max):
    """Accept a range, then return a function for validation.
    This function exists to faciliate using validation with custom args

    Argument explanation:
        - _min - an integer of the minimum acceptable range
        - _max - an integer of the maximum acceptable range
    """

    def validate(value):
        my_length = len(value)

        if my_length < _min or my_length > _max:

            msg = '%(value)s must be of length >= %(min)s and <= ' \
                  '%(max)s. Input was of length %(my_length)s'

            params = {
                'value': value,
                'min': _min,
                'max': _max,
                'my_length': my_length,
            }
            raise ValidationError(
                _(msg), params=params,
            )

    return validate


# ****************** Forms

class ContactForm(forms.Form):
    """Form fields required of any PaymentProfile"""

    def create_payment_profile(self, customer_profile):
        """Create a Credit Card Payment Profile using this form
        customer_profile must be a CustomerProfile instance
        """

        # Confirm that the form has been cleaned before processing
        if not hasattr(self, 'cleaned_data'):
            msg = 'create_contact_dictionary() may only be run on ' \
                  'VALIDATED forms. This form wasn\'t validated'
            raise ValueError(msg)

        self.contact_dictionary = {
            'address': self.cleaned_data['address'],
            'city': self.cleaned_data['city'],
            'state': self.cleaned_data['state'],
            'zip_code': self.cleaned_data['zip_code'],
            'phone': self.cleaned_data['phone_number']
        }

    customer_type = forms.ChoiceField(choices=CustomerType.as_tuple)
    first_name = forms.CharField(
        max_length=constants.MAX_FIRST_NAME_CHARS,
        label='Your First Name')
    last_name = forms.CharField(
        max_length=constants.MAX_LAST_NAME_CHARS,
        label='Your Last Name')
    company_name = forms.CharField(
        max_length=constants.MAX_COMPANY_NAME_CHARS)
    address = forms.CharField(
        max_length=constants.MAX_ADDRESS_CHARS)
    city = forms.CharField(
        max_length=constants.MAX_CITY_CHARS)
    state = forms.CharField(
        max_length=constants.MAX_STATE_CHARS)
    zip_code = forms.CharField(
        max_length=constants.MAX_ZIP_CODE_CHARS)
    country = forms.CharField(
        max_length=constants.MAX_COUNTRY_CHARS)
    phone_number = forms.CharField(
        max_length=constants.MAX_PHONE_NUMBER_CHARS)
    default_method = forms.BooleanField(
        widget=forms.CheckboxInput(),
        label="Save this as the default payment method?",
        required=False,
        initial=True)

    final_key_order = [
        'customer_type',
        'first_name',
        'last_name',
        'company_name',
        'address',
        'city',
        'state',
        'zip_code',
        'country',
        'phone_number',
        'default_method'
    ]


class CreditCardForm(ContactForm):
    """Save a payment profile with a credit card"""

    @staticmethod
    def two_digits(i):
        """Convert an integer into a 2 digit string"""
        if i < 10:
            return '0' + str(i)

        return str(i)

    def __init__(self, *args, **kwargs):
        """Inherit the fields of ContactForm, but rearrange the field order
        so that the fields of CreditCard appear first"""
        super().__init__(*args, **kwargs)

        # Set expiration months and year choices
        self.fields['expiration_month'].choices = [
            (self.two_digits(i),
             calendar.month_name[i]) for i in range(1, 13)]

        current_year = datetime.datetime.now().year

        self.fields['expiration_year'].choices = [
            (str(i), i) for i in range(current_year, current_year + 50)]

        # Set the order of the form fields

        front_order = [
            'credit_card_number',
            'expiration_month',
            'expiration_year',
            'card_code'
        ]

        fields = OrderedDict()
        # final_key_order is a saved attribute from ContactForm
        merged_order = front_order + self.final_key_order

        for key in merged_order:
            fields[key] = self.fields.pop(key)
        self.fields = fields

    def clean(self):
        """Use the default clean(), then confirm that a valid month
        and year were entered.
        """

        # start override
        expiration_month = int(self.data['expiration_month'])
        expiration_year = int(self.data['expiration_year'])

        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month

        if expiration_year < current_year:
            msg = _('The expiration year must be >={}')
            self.add_error('expiration_year', msg.format(current_year))

        if (expiration_year == current_year and
                current_month > expiration_month):
            msg = _('The card is past its expiration month. The card '
                    'expired in {}, but it\'s currently {}')
            self.add_error('expiration_month', msg.format(
                calendar.month_name[expiration_month],
                calendar.month_name[current_month]))

        # use the default cleaning method
        # This is at the end of the file to prevent invalid fields
        # from being cleaned up before finding the error
        super().clean()

    def create_payment_profile(self, customer_profile):
        """Create a Credit Card Payment Profile using this form

        customer_profile must be a CustomerProfile instance
        """

        super().create_payment_profile(customer_profile)

        expiration = '{}-{}'.format(
            self.cleaned_data['expiration_month'],
            self.cleaned_data['expiration_year'])

        try:
            profile_id = customer_profile.create_customer_payment_profile_credit_card(  # noqa
                self.cleaned_data['credit_card_number'],
                expiration,
                self.cleaned_data['card_code'],
                CustomerType[self.cleaned_data['customer_type']],
                self.cleaned_data['first_name'],
                self.cleaned_data['last_name'],
                self.contact_dictionary,
                self.cleaned_data['company_name'],
                False,
                self.cleaned_data['default_method'])

            return profile_id
        except AuthorizeNetError as err:
            return str(err)

    # Form fields

    credit_card_number = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'number'}),
        validators=[
            length_range(
                constants.MIN_CREDIT_CARD_DIGITS,
                constants.MAX_CREDIT_CARD_DIGITS),
            is_integer])
    expiration_month = forms.ChoiceField()
    expiration_year = forms.ChoiceField()
    card_code = forms.CharField(
        validators=[
            length_range(
                constants.MIN_CARD_CODE_DIGITS,
                constants.MAX_CARD_CODE_DIGITS)])


class ECheckForm(ContactForm):
    """Save a payment profile with an eCheck"""

    def __init__(self, *args, **kwargs):
        """Inherit the fields of ContactForm, but rearrange the field order
        so that the fields of CreditCard appear first"""
        super().__init__(*args, **kwargs)

        front_order = [
            'account_type',
            'routing_number',
            'account_number',
            'name_on_account',
            'bank_name'
        ]

        fields = OrderedDict()
        # final_key_order is a saved attribute from ContactForm
        merged_order = front_order + self.final_key_order

        for key in merged_order:
            fields[key] = self.fields.pop(key)
        self.fields = fields

    def create_payment_profile(self, customer_profile):
        """Create a Credit Card Payment Profile using this form

        customer_profile must be a CustomerProfile instance
        """

        super().create_payment_profile(customer_profile)

        try:
            profile_id = customer_profile.create_customer_payment_profile_echeck(  # noqa
                AccountType[self.cleaned_data['account_type']],
                self.cleaned_data['routing_number'],
                self.cleaned_data['account_number'],
                self.cleaned_data['name_on_account'],
                self.cleaned_data['bank_name'],
                CustomerType[self.cleaned_data['customer_type']],
                self.cleaned_data['first_name'],
                self.cleaned_data['last_name'],
                self.contact_dictionary,
                self.cleaned_data['company_name'],
                False,
                self.cleaned_data['default_method'])

            return profile_id
        except AuthorizeNetError as err:
            return str(err)

    # Form fields

    account_type = forms.ChoiceField(choices=AccountType.as_tuple)
    routing_number = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'number'}),
        validators=[
            length_range(
                constants.ABA_DIGITS,
                constants.ABA_DIGITS),
            is_integer])
    account_number = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'number'}),
        validators=[is_integer])
    name_on_account = forms.CharField(
        max_length=constants.MAX_NAME_ON_ACCOUNT_CHARS)
    bank_name = forms.CharField(
        max_length=constants.MAX_BANK_NAME_CHARS)
