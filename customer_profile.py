from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *
from django.db import models
from payment_authorizenet.enums import CustomerType, ValidationMode
from payment_authorizenet.merchant_auth import AuthNet, AuthorizeNetError
from payment_authorizenet.payment_profile import PaymentProfile
from payment_authorizenet.transaction import Transaction

OK = "Ok"


class CustomerProfile(AuthNet):
    """A class based implementation to relate a Django model to the
    creation of a CustomerProfile (aka CIM, Customer Information Manager)"""

    def __init__(self, instance, *args, **kwargs):
        """Attach a django model to the insatnce attribute of this class"""
        super().__init__(*args, **kwargs)

        if not hasattr(instance, 'authorizenet_customer_profile_id'):
            msg = 'Models used to create a customer profile must contain ' \
                  'an authorizenet_customer_profile_id attribute'
            raise ValueError(msg)

        if not issubclass(type(instance), models.Model):
            raise ValueError('instance must be a Django model')

        self.instance = instance

    def charge_customer_profile(self, paymentProfileId, amount, ref_id):

        # create a customer payment profile
        profileToCharge = apicontractsv1.customerProfilePaymentType()
        profileToCharge.customerProfileId = str(
            self.instance.authorizenet_customer_profile_id)
        profileToCharge.paymentProfile = apicontractsv1.paymentProfile()
        profileToCharge.paymentProfile.paymentProfileId = paymentProfileId

        transactionrequest = apicontractsv1.transactionRequestType()
        transactionrequest.transactionType = "authCaptureTransaction"
        transactionrequest.amount = amount
        transactionrequest.profile = profileToCharge

        createtransactionrequest = apicontractsv1.createTransactionRequest()
        createtransactionrequest.merchantAuthentication = self.merchantAuth
        createtransactionrequest.refId = str(ref_id)

        createtransactionrequest.transactionRequest = transactionrequest
        createtransactioncontroller = createTransactionController(
            createtransactionrequest)
        createtransactioncontroller.execute()

        response = createtransactioncontroller.getresponse()

        return Transaction(response)

    def create_customer_profile(self, email):
        """
        This information is viewed on the authorize.net website as
        Customer Information Manager (CIM). The API confusingly references
        the CIM as a CustomerProfile. They are synonymous.
        """

        createCustomerProfile = apicontractsv1.createCustomerProfileRequest()
        createCustomerProfile.merchantAuthentication = self.merchantAuth

        createCustomerProfile.profile = apicontractsv1.customerProfileType(
            str(self.instance.pk),
            str(self.instance),
            email)

        controller = createCustomerProfileController(createCustomerProfile)
        controller.execute()

        response = controller.getresponse()

        if response.messages.resultCode == OK:
            print("Successfully created a customer profile with id: {}".format(
                response.customerProfileId))
            self.instance.authorizenet_customer_profile_id = int(
                response.customerProfileId)
            self.instance.save()
            print('saved', self.instance)
            return True
        else:
            raise AuthorizeNetError(response.messages.message[0]['text'].text)

    def make_billTo(
            first_name,
            last_name,
            company_name,
            address,
            city,
            state,
            zip_code,
            country,
            phone):

        billTo = apicontractsv1.customerAddressType()
        billTo.firstName = first_name
        billTo.lastName = last_name
        billTo.company = company_name
        billTo.address = address
        billTo.city = city
        billTo.state = state
        billTo.zip = zip_code
        billTo.country = country
        billTo.phoneNumber = phone

        return billTo

    def make_creditCard(
            credit_card,
            expiration_date,
            card_code):
        """Add/Edit a credit card details """

        payment = apicontractsv1.paymentType()

        creditCard = apicontractsv1.creditCardType()
        creditCard.cardNumber = credit_card
        creditCard.expirationDate = expiration_date
        creditCard.cardCode = card_code
        payment.creditCard = creditCard

        return payment

    def make_bankAccount(
            account_type,
            routing_number,
            account_number,
            name_on_account,
            bank_name):

        bankAccount = apicontractsv1.bankAccountType()
        bankAccount.accountType = account_type.value
        bankAccount.routingNumber = routing_number
        bankAccount.accountNumber = account_number
        bankAccount.nameOnAccount = name_on_account
        bankAccount.bankName = bank_name

        payment = apicontractsv1.paymentType()
        payment.bankAccount = bankAccount

        return payment

    def create_customer_payment_profile(
            self,
            payment,
            customer_type,
            first_name,
            last_name,
            contact_dictionary,
            company_name,
            set_as_default,
            validation_mode=ValidationMode.liveMode):
        """Add a payment profile on the CIM"""

        if not isinstance(customer_type, CustomerType):
            msg = 'customer_type must be a CustomerType enum. ' \
                  'Your type is {}\n{}'
            raise ValueError(msg.format(type(customer_type), customer_type))

        address = contact_dictionary.get('address')
        city = contact_dictionary.get('city')
        state = contact_dictionary.get('state')
        zip_code = contact_dictionary.get('zip_code')
        country = 'US'
        phone = contact_dictionary.get('phone')

        profile = apicontractsv1.customerPaymentProfileType()
        profile.payment = payment
        profile.customerType = customer_type.value
        profile.billTo = CustomerProfile.make_billTo(
            first_name, last_name, company_name, address,
            city, state, zip_code, country, phone)

        createCustomerPaymentProfile = apicontractsv1.createCustomerPaymentProfileRequest()  # noqa
        createCustomerPaymentProfile.merchantAuthentication = self.merchantAuth
        createCustomerPaymentProfile.paymentProfile = profile
        createCustomerPaymentProfile.customerProfileId = str(
            self.instance.authorizenet_customer_profile_id)
        createCustomerPaymentProfile.validationMode = validation_mode.value

        controller = createCustomerPaymentProfileController(
            createCustomerPaymentProfile)
        controller.execute()

        response = controller.getresponse()

        if response.messages.resultCode == OK:
            msg = 'Successfully created a customer payment profile with id: {}'
            print(msg.format(response.customerPaymentProfileId))

            if set_as_default:
                self.instance.authorizenet_default_payment_profile_id = int(
                    response.customerPaymentProfileId)
                self.instance.save()
            return self.instance.authorizenet_default_payment_profile_id
        else:
            raise AuthorizeNetError(response.messages.message[0]['text'].text)

    def create_contact_dictionary(self, use_model_address, args_dictionary):
        """Create contact information as a disctionary

        use_model_address expects a boolean argument
        pass kwargs from an argument for the kwargs_dictionary argument"""

        if not use_model_address:
            # If the model contains address information but
            # you don't want to use it,
            # or the model doesn't have address indormation in this format
            # then set the flag use_model_address to False
            if args_dictionary is None:
                msg = 'Expected kwargs with address details when ' \
                      'use_model_address is False'
                raise ValueError(msg)

            address = args_dictionary.get('address')
            city = args_dictionary.get('city')
            state = args_dictionary.get('state')
            zip_code = args_dictionary.get('zip_code')
            phone = args_dictionary.get('phone')
        else:
            # Use address information from the model
            address = self.instance.address

            if hasattr(self.instance, 'address2'):
                address = address + self.instance.address2

            city = self.instance.city
            state = self.instance.state
            zip_code = self.instance.zip_code
            phone = self.instance.phone

        return {
            'address': address,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'phone': phone
        }

    def create_customer_payment_profile_credit_card(
            self,
            credit_card,
            expiration_date,
            card_code,
            customer_type,
            first_name,
            last_name,
            contact_dictionary=None,
            company_name=None,
            use_model_address=True,
            set_as_default=True,
            validation_mode=ValidationMode.liveMode):
        """Add a credit card payment profile on the CIM"""

        contact_dictionary = self.create_contact_dictionary(
            use_model_address, contact_dictionary)

        payment = CustomerProfile.make_creditCard(
            credit_card, expiration_date, card_code)

        return self.create_customer_payment_profile(
            payment,
            customer_type,
            first_name,
            last_name,
            contact_dictionary,
            company_name,
            set_as_default,
            validation_mode)

    def create_customer_payment_profile_echeck(
            self,
            account_type,
            routing_number,
            account_number,
            name_on_account,
            bank_name,
            customer_type,
            first_name,
            last_name,
            contact_dictionary=None,
            company_name=None,
            use_model_address=True,
            set_as_default=True,
            validation_mode=ValidationMode.liveMode):
        """Add an eCheck payment profile on the CIM"""

        contact_dictionary = self.create_contact_dictionary(
            use_model_address, contact_dictionary)

        payment = CustomerProfile.make_bankAccount(
            account_type, routing_number, account_number,
            name_on_account, bank_name)

        return self.create_customer_payment_profile(
            payment,
            customer_type,
            first_name,
            last_name,
            contact_dictionary,
            company_name,
            set_as_default,
            validation_mode)

    def delete_customer_profile(self):

        deleteCustomerProfile = apicontractsv1.deleteCustomerProfileRequest()
        deleteCustomerProfile.merchantAuthentication = self.merchantAuth
        deleteCustomerProfile.customerProfileId = str(
            self.instance.authorizenet_customer_profile_id)

        controller = deleteCustomerProfileController(deleteCustomerProfile)
        controller.execute()

        response = controller.getresponse()

        if response.messages.resultCode == OK:
            print(
                'deleted customer profile',
                self.instance.authorizenet_customer_profile_id)
            self.instance.authorizenet_customer_profile_id = None
            return True
        else:
            print(response.messages.message[0]['text'].text)
            raise AuthorizeNetError(response.messages.resultCode)

    def delete_customer_payment_profile(self, customerPaymentProfileId):
        """Delete a payment profile with a known ID"""

        action = apicontractsv1.deleteCustomerPaymentProfileRequest()
        action.merchantAuthentication = self.merchantAuth
        action.customerProfileId = str(
            self.instance.authorizenet_customer_profile_id)
        action.customerPaymentProfileId = customerPaymentProfileId

        controller = deleteCustomerPaymentProfileController(
            action)
        controller.execute()

        response = controller.getresponse()

        if response.messages.resultCode == OK:
            return True
        else:
            print(response.messages.message[0]['text'].text)
            raise AuthorizeNetError(response.messages.resultCode)

    def get_customer_profile(self):
        """Used to retrive payment profiles"""

        getCustomerProfile = apicontractsv1.getCustomerProfileRequest()
        getCustomerProfile.merchantAuthentication = self.merchantAuth
        getCustomerProfile.customerProfileId = str(
            self.instance.authorizenet_customer_profile_id)
        controller = getCustomerProfileController(getCustomerProfile)
        controller.execute()

        self.customer_profile = controller.getresponse()
        response = self.customer_profile

        if (self.customer_profile.messages.resultCode == OK):
            if hasattr(self.customer_profile, 'profile'):
                if hasattr(self.customer_profile.profile, 'paymentProfiles'):
                    ppfs = self.customer_profile.profile.paymentProfiles
                    self.payment_profiles = [PaymentProfile(pp) for pp in ppfs]

            # This section needs to be abstracted into objects
            # similar to PaymentProfile
            if hasattr(response, 'profile'):
                if hasattr(response.profile, 'shipToList'):
                    for ship in response.profile.shipToList:
                        print("Shipping Details:")
                        print("First Name %s" % ship.firstName)
                        print("Last Name %s" % ship.lastName)
                        print("Address %s" % ship.address)
                        print(
                            "Customer Address ID %s" % ship.customerAddressId)
            if hasattr(response, 'subscriptionIds'):
                if hasattr(response.subscriptionIds, 'subscriptionId'):
                    print ("list of subscriptionid:")
                    for subscriptionid in (
                            response.subscriptionIds.subscriptionId):
                        print(subscriptionid)
        else:
            raise AuthorizeNetError(response.messages.resultCode)

    def update_customer_payment_profile(
            self,
            payment,
            customerPaymentProfileId,
            first_name,
            last_name,
            contact_dictionary,
            company_name,
            set_as_default,
            validation_mode):

        print('Updating customer payment profile', customerPaymentProfileId)

        address = contact_dictionary.get('address')
        city = contact_dictionary.get('city')
        state = contact_dictionary.get('state')
        zip_code = contact_dictionary.get('zip_code')
        country = 'US'
        phone = contact_dictionary.get('phone')

        paymentProfile = apicontractsv1.customerPaymentProfileExType()
        paymentProfile.billTo = CustomerProfile.make_billTo(
            first_name, last_name, company_name, address,
            city, state, zip_code, country, phone)
        paymentProfile.payment = payment
        paymentProfile.customerPaymentProfileId = customerPaymentProfileId

        action = apicontractsv1.updateCustomerPaymentProfileRequest()
        action.merchantAuthentication = self.merchantAuth
        action.paymentProfile = paymentProfile
        action.customerProfileId = str(
            self.instance.authorizenet_customer_profile_id)
        action.validationMode = validation_mode.value

        controller = updateCustomerPaymentProfileController(action)
        controller.execute()

        response = controller.getresponse()

        if response.messages.resultCode == OK:
            msg = 'Successfully created a customer payment profile with id: {}'
            print(msg.format(customerPaymentProfileId))

            if set_as_default:
                self.instance.authorizenet_default_payment_profile_id = int(
                    customerPaymentProfileId)
                self.instance.save()

            return customerPaymentProfileId
        else:
            raise AuthorizeNetError(response.messages.message[0]['text'].text)

    def update_customer_payment_profile_credit_card(
            self,
            customerPaymentProfileId,
            credit_card,
            expiration_date,
            card_code,
            customer_type,
            first_name,
            last_name,
            contact_dictionary=None,
            company_name=None,
            use_model_address=True,
            set_as_default=True,
            validation_mode=ValidationMode.liveMode):

        contact_dictionary = self.create_contact_dictionary(
            use_model_address, contact_dictionary)

        payment = CustomerProfile.make_creditCard(
            credit_card, expiration_date, card_code)

        return self.update_customer_payment_profile(
            payment,
            customerPaymentProfileId,
            first_name,
            last_name,
            contact_dictionary,
            company_name,
            set_as_default,
            validation_mode)

    def update_customer_payment_profile_echeck(
            self,
            customerPaymentProfileId,
            account_type,
            routing_number,
            account_number,
            name_on_account,
            bank_name,
            customer_type,
            first_name,
            last_name,
            contact_dictionary=None,
            company_name=None,
            use_model_address=True,
            set_as_default=True,
            validation_mode=ValidationMode.testMode):
        """Update a customerPaymentProfile to an echeck
        ValidationMode.testMode is used because eCheck does not currently
        support liveMode"""

        contact_dictionary = self.create_contact_dictionary(
            use_model_address, contact_dictionary)

        payment = CustomerProfile.make_bankAccount(
            account_type, routing_number, account_number,
            name_on_account, bank_name)

        return self.update_customer_payment_profile(
            payment,
            customerPaymentProfileId,
            first_name,
            last_name,
            contact_dictionary,
            company_name,
            set_as_default,
            validation_mode)
