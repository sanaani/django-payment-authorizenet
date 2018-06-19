from authorizenet import apicontractsv1
from django.conf import settings


class AuthNet:

    def __init__(self):
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = settings.AUTHORIZE_NET_API_LOGIN_ID
        merchantAuth.transactionKey = settings.AUTHORIZE_NET_TRANSACTION_KEY

        self.merchantAuth = merchantAuth


class AuthorizeNetError(Exception):
    """Exceptions related to Authorize.net operations
    To use the exception, just do this: raise AuthorizeNetError('Message here')
    """

    pass
