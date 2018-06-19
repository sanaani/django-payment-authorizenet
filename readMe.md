# Django Payment AuthorizeNet

This repository implements the Authorize.NET payment gateway as a Django app.

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
```

## Assumptions

CustomerProfile in customer_profile.py fundamentally assumes that a Djando model exists, which should represent all aspects of transactions with Authorize.net. For many businesses, this will be a Customer model or something similarly named.

The django model used must contain a field named *authorizenet_customer_profile_id*.