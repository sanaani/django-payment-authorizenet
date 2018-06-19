from enum import Enum


class PaymentType(Enum):
    creditCard = 'creditCard'
    bankAccount = 'bankAccount'


class PaymentProfile:

    def __init__(self, response):
        super().__init__()

        self.customer_payment_profile_id = response.customerPaymentProfileId
        self.payment = Payment(response.payment)

    def __str__(self):
        return '{}: {}'.format(self.customer_payment_profile_id, self.payment)


class CreditCard:
    """Stores details of an credit card in PaymentProfile"""
    def __init__(self, creditCard):
        super().__init__()

        self.card_number = creditCard.cardNumber
        self.card_expiration_date = creditCard.expirationDate
        self.card_type = creditCard.cardType

        if hasattr(creditCard, 'issuerNumber'):
            self.issuer_number = creditCard.issuerNumber


class BankAccount:
    """Stores details of an eCheck in PaymentProfile"""
    def __init__(self, bank_account):
        super().__init__()

        self.account_type = bank_account.accountType
        self.routing_number = bank_account.routingNumber
        self.account_number = bank_account.accountNumber
        self.name_on_account = bank_account.nameOnAccount
        self.echeck_type = bank_account.echeckType

        if hasattr(bank_account, 'bankName'):
            self.bank_name = bank_account.bankName


class Payment:

    credit_card = None
    bank_account = None
    payment_type = 'Not set'

    def __init__(self, payment):
        super().__init__()
        self.payment = payment

        if hasattr(self.payment, PaymentType.creditCard.value):
            self.credit_card = CreditCard(payment.creditCard)
            self.payment_type = 'Credit Card'
        elif hasattr(self.payment, PaymentType.bankAccount.value):
            self.bank_account = BankAccount(payment.bankAccount)
            self.payment_type = 'Bank Account'

    def __str__(self):
        return self.payment_type
