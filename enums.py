from enum import Enum


# Enums for createCustomerPaymentProfileRequest ********

class CustomerType(Enum):
    individual = 'individual'
    business = 'business'


class AccountType(Enum):
    checking = 'checking'
    savings = 'savings'
    businessChecking = 'businessChecking'


class ECheckType(Enum):
    PPD = 'PPD'
    WEB = 'WEB'
    CCD = 'CCD'


class ValidationMode(Enum):
    testMode = 'testMode'
    liveMode = 'liveMode'
