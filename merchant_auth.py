from authorizenet import apicontractsv1
from django.conf import settings
from payment_authorizenet.enums import ServerMode


class AuthorizeNetError(Exception):
    """Exceptions related to Authorize.net operations
    To use the exception, just do this: raise AuthorizeNetError('Message here')
    """

    pass


class AuthNet:
    """This class is intended to be inherited by any class wishing to perform
    operations on the Authorize.net gateway.
    You'll always need to supply credentials, which this class sets
    and makes available from settings"""

    def __init__(self):

        # ********** Set Authentication Credentials *************

        merchantAuth = apicontractsv1.merchantAuthenticationType()

        if not hasattr(settings, 'AUTHORIZE_NET_API_LOGIN_ID'):
            msg = 'AUTHORIZE_NET_API_LOGIN_ID does not exist ' \
                  'in your Django settings'
            raise AuthorizeNetError(msg)

        merchantAuth.name = settings.AUTHORIZE_NET_API_LOGIN_ID

        if not hasattr(settings, 'AUTHORIZE_NET_TRANSACTION_KEY'):
            msg = 'AUTHORIZE_NET_TRANSACTION_KEY does not exist ' \
                  'in your Django settings'
            raise AuthorizeNetError(msg)

        merchantAuth.transactionKey = settings.AUTHORIZE_NET_TRANSACTION_KEY

        self.merchantAuth = merchantAuth

        # ********** Set the POST URL for the controllers *************

        SANDBOX = 'https://apitest.authorize.net/xml/v1/request.api'
        PRODUCTION = 'https://api2.authorize.net/xml/v1/request.api'

        if not hasattr(settings, 'SERVER_MODE'):
            msg = 'You must set SERVER_MODE in your Django settings to a ' \
                  'ServerMode enum: {}}'
            raise AuthorizeNetError(msg.format(ServerMode.str_list()))

        if settings.SERVER_MODE == ServerMode.production.value:
            self.post_url = PRODUCTION
        else:  # any evironment that's not production should use sandbox
            self.post_url = SANDBOX
