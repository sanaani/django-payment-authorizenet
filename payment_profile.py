from payment_authorizenet.enums import PaymentProfileType


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

    def __str__(self):
        return '{} {}'.format(self.card_type, self.card_number)


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

    def __str__(self):
        return '{} {}'.format(self.bank_name, self.account_number)


class Payment:

    credit_card = None
    bank_account = None
    payment_type = 'Not set'

    def __init__(self, payment):
        super().__init__()
        self.payment = payment

        if hasattr(self.payment, PaymentProfileType.creditCard.name):
            print('setting credit card details')
            self.credit_card = CreditCard(payment.creditCard)
            self.payment_type = PaymentProfileType.creditCard
            self.output = str(self.credit_card)
            self.entity = self.credit_card.card_type
            self.account_number = self.credit_card.card_number
        elif hasattr(self.payment, PaymentProfileType.bankAccount.name):
            print('setting bank account details')
            self.bank_account = BankAccount(payment.bankAccount)
            self.payment_type = PaymentProfileType.bankAccount
            self.output = str(self.bank_account)
            self.entity = self.bank_account.bank_name
            self.account_number = self.bank_account.account_number
        else:
            print('no payment was set')

    def __str__(self):
        return self.output
