# Django Payment AuthorizeNet

The goal of the project is to use your existing Django model(s) to create, view or modify transactions with the Authorize.net gateway. Only one migration within your current project will be required (see Assumptions).

The extant work focuses on working with the Customer Information Manager (CIM). If you see a missing feature, then please consider contributing!

This project is very new (started May 2018). If you see a problem or would like to contribute, then please email Shaun Overton at info@onestepremoved.com.

## Supported library versions

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
    'payment_authorizenet',
    ...
]

# Recognized values for SERVER_MODE are controlled by the ServerMode enumeration
# *values* in [enums.py](/blob/master/enums.py). The example below shows
# ServerMode.development.value
SERVER_MODE = 'Development'
```

## Assumptions

CustomerProfile in customer_profile.py fundamentally assumes that a Djando model exists and is being passed to it. For most businesses, this will be a Customer model or something similar.

The django passed to CustomerProfile must contain a field named *authorizenet_customer_profile_id*.


## Styling syntax in the code

The Authorize.net API uses camel-case syntax (eg, 'myVariable'), whereas most Python code is written with underscores (eg: 'my_variable'). This project attempts to distinguish between its internal variables and authorize.net SDK related variables by using:

1. Camel-case syntax (eg, 'myVariable') applies to code that uses direct calls to the SDK. An example is in [customerprofile.py](/blob/master/customer_profile.py): `profileToCharge.paymentProfile = apicontractsv1.paymentProfile()`.

   The code generally follows this camel case approach for SDK variables, but some code varies because the choice to distinguish the syntax was not made until it started causing confusion. I hope to gradually enforce this syntax across all of the code.

2. Underscore syntax (eg, 'my_variable') is used for everthing that does not directly call the SDK. Examples are objects returned that are intended as read-only (like )