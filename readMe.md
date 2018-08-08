# Django Payment AuthorizeNet

The goal of the project is to use your existing Django model(s) to create, view or modify transactions with the Authorize.net gateway. Only one migration within your current project will be required (see Assumptions).

The extant work focuses on working with the Customer Information Manager (CIM). If you see a missing feature, then please consider contributing!

This project is very new (started May 2018). If you see a problem, then please post them directly in the [issues](https://github.com/sanaani/django-payment-authorizenet/issues) sections.

## Minimum Supported Dependencies

Django 2.0
Authorizenet SSF v1
Python 3.6

## Setup

Make the following changes to your django settings file

```
AUTHORIZE_NET_API_LOGIN_ID = 'your api login id here'
AUTHORIZE_NET_TRANSACTION_KEY = 'your transaction key here'
AUTHORIZE_NET_KEY = 'your key here'

# add authorizenet and payment_authorizenet to your INSTALLED_APPS list
INSTALLED_APPS = [
    ...
    'authorizenet',
    'django-payment-authorizenet',
    ...
]

# Recognized values for SERVER_MODE are controlled by the ServerMode enumeration
# *values* in [enums.py](/blob/master/enums.py). The example below shows
# ServerMode.development.value
SERVER_MODE = 'Development'
```

## Assumptions

CustomerProfile in customer_profile.py fundamentally assumes that a Djando model exists and is being passed to it. For most businesses, this will be a Customer model or something similar.

The django model passed to CustomerProfile must contain a field named *authorizenet_customer_profile_id*.


## Styling syntax in the code

The Authorize.net API uses camel-case syntax (eg, 'myVariable'), whereas most Python code is written with underscores (eg: 'my_variable'). This project attempts to distinguish between its internal variables and authorize.net SDK related variables by using:

1. Camel-case syntax (eg, `myVariable`) applies to code that uses direct calls to the SDK. An example is in [customerprofile.py](customer_profile.py): `profileToCharge.paymentProfile = apicontractsv1.paymentProfile()`.

   The code generally follows this camel case approach for SDK variables, but some code varies because the choice to distinguish the syntax was not made until it started causing confusion. I hope to gradually enforce this syntax across all of the code.

2. Underscore syntax (eg, `my_variable`) is used for everthing that does not directly call the SDK. Examples are objects returned that are intended as read-only

## Help Me Help You

Support this project by registering any new Authorize.net accounts using [this link](http://reseller.authorize.net/application/?resellerId=104913). Your costs are identical to registering directly with Authorize.net, but I earn commissions based on your use of the software. 

http://reseller.authorize.net/application/?resellerId=104913

Or, if you already have an existing Authorize.net account...

### Add a New Merchant Service Processor (MSP) or Switch Your MSP for Better Pricing

Email Shaun Overton at info@onestepremoved.com with your company information and phone number. My MSP solution integrates seamlessly with Authorize.net.
