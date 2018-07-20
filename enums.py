from enum import Enum


class EnumTuple(Enum):

    @classmethod
    def as_tuple(cls):
        """Used for making enums available as choices in Forms"""
        return tuple((x.name, x.value) for x in cls)

    @classmethod
    def as_tuple_with_all(cls):
        setup = [(x.name, x.value) for x in cls]
        setup.append(('all', 'All'))
        return tuple(x for x in setup)

    @classmethod
    def str_list(cls):
        # List all enum values with a space after them, then trim the
        # trailing whitespace
        spaced_names = ''.join(x.value + ' ' for x in cls).strip()

        SPACE = ' '
        COMMA_SPACE = ', '

        # put commas in the appropriate locations
        return spaced_names.replace(SPACE, COMMA_SPACE)


class CustomerType(EnumTuple):
    individual = 'Individual'
    business = 'Business'


class AccountType(EnumTuple):
    businessChecking = 'Business Checking'
    checking = 'Checking'
    savings = 'Saving'


class ECheckType(EnumTuple):
    PPD = 'PPD'
    WEB = 'WEB'
    CCD = 'CCD'


class PaymentProfileType(EnumTuple):
    """Type of Payment Profile"""
    bankAccount = 'Bank Account'
    creditCard = 'Credit Card'


class ServerMode(EnumTuple):
    """
    Use this enum within your Django settings file
    Create a variable SERVER_MODE in settings
    Example: SERVER_MODE = ServerMode.development.value

    ServerMode is frequently used with the authorizenet SDK to
    configure the posting URL of a controller. See customer_profile
    for examples
    """

    development = 'Development'  # testing on your local machine
    staging = 'Staging'  # a semi-private server intended for testing
    production = 'Production'  # client facting software


class ValidationMode(EnumTuple):
    testMode = 'Test Mode'
    liveMode = 'Live Mode'
