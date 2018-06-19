import json
import ssl
import urllib.request


class Transaction:
    """A transaction is returned with completion or failure info"""

    OK = "Ok"
    FAILURE = 'Failure'
    APPROVED = 'Approved'
    CODE = 'code'

    code_ref_url = 'https://developer.authorize.net/api/'\
                   'reference/dist/json/responseCodes.json'

    def __init__(self, response):
        """Pass the response to initialize the Transaction object"""
        super().__init__()

        # default SSL used b/c the certificate is only 128 bit, which throws
        # this exception if relying on the Authorize.net certificate
        # urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY
        # _FAILED] certificate verify failed (_ssl.c:748)>

        ssl._create_default_https_context = ssl._create_unverified_context

        with urllib.request.urlopen(self.code_ref_url) as url:
            data = json.loads(url.read().decode())
            approval_dict = list(filter(
                lambda x: x['code'] == '1', data))

        if response is not None:

            self.transaction_response = TransactionResponse(response)

            response_code = self.transaction_response.response_code
            self.approval_code = int(approval_dict[0][self.CODE])

            if response_code == self.approval_code:
                self.result = self.APPROVED
            else:
                self.result = self.FAILURE

            print('result is', self.result)

        else:
            self.error_code = None
            self.error_text = 'Null response from Authorize.net'


class TransactionResponse:

    fields = {
        'responseCode': 'response_code',
        'authCode': 'auth_code',
        'avsResultCode': 'avs_result_code',
        'cvvResultCode': 'cvv_result_code',
        'cavv_result_code': 'cavv_result_code',
        'transId': 'transaction_id',
        'refTransID': 'reference_transaction_id',
        'transHash': 'transaction_hash',
        'testRequest': 'test_request',
        'accountNumber': 'account_number',
        'accountType': 'account_type',
        'transHashSha2': 'transaction_hash_sha2',

    }

    def __init__(self, response):
        """Pass the response to initialize the TransactionResponse object"""
        super().__init__()

        tr = response.transactionResponse

        for k, v in self.fields.items():

            if hasattr(tr, k):
                setattr(self, v, getattr(tr, k))

        if hasattr(tr, 'errors'):
            self.errors = [Error(an_error) for an_error in tr.errors]
        else:
            self.errors = None

        if hasattr(tr, 'profile'):
            self.profile = Profile(response)
        else:
            self.profile = None


class Error:

    fields = {
        'errorCode': 'error_code',
        'errorText': 'error_text'
    }

    def __init__(self, an_error):
        """Convert the response into a defined object"""
        for k, v in self.fields.items():

            if hasattr(an_error, k):
                setattr(self, v, getattr(an_error, k))


class Profile:
    """Store customer and payment profile info of a Transaction"""

    fields = {
        'customerProfileId': 'customer_profile_id',
        'customer_payment_profile_id': 'customer_payment_profile_id',
        'avsResultCode': 'avs_result_code',
        'cvvResultCode': 'cvv_result_code',
        'cavv_result_code': 'cavv_result_code',
        'transId': 'transaction_id',
        'refTransID': 'reference_transaction_id',
        'transHash': 'transaction_hash',
        'testRequest': 'test_request',
        'accountNumber': 'account_number',
        'accountType': 'account_type',
        'transHashSha2': 'transaction_hash_sha2',

    }

    def __init__(self, response):

        profile = response.transactionResponse.profile

        for k, v in self.fields.items():

            if hasattr(profile, k):
                setattr(self, v, getattr(profile, k))
