
import base64
import datetime
import hashlib
import hmac
from bs4 import BeautifulSoup
import requests

from mail_sender_daemon.exceptions import UnvalidatedAddrError
from . import _BaseProvider


class _BaseAmazonSES():
    def __init__(self, api_access_key, api_secret_key):
        self._api_access_key = api_access_key
        self._api_secret_key = api_secret_key

    def _build_request_headers(self):
        """
        Build needed request header for AWS
        """
        date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        return {
            "Content-type": "application/x-www-form-urlencoded",
            "Date": date,
            "X-Amzn-Authorization": (
                "AWS3-HTTPS AWSAccessKeyId={}, Algorithm=HMACSHA256, "
                "Signature={}"
            ).format(self._api_access_key, self._build_signature(date))
        }

    def _build_signature(self, date):
        """
        AWS signature algorithm
        """
        h = hmac.new(
            key=self._api_secret_key.encode(), msg=date.encode(),
            digestmod=hashlib.sha256
        )
        return base64.b64encode(h.digest()).decode()


class AmazonSES(_BaseAmazonSES, _BaseProvider):
    def __init__(self, api_domain, premium=False, *args, **kwargs):
        """
        param api_domain: Amazon API domain
        param premium: is the account a premium account. If premium, authorized
                       addresses will not be checked before sending it.
        """
        self.api_domain = api_domain
        self.premium = premium
        super().__init__(*args, **kwargs)

        self.validation_strategy = _AmazonSESValidation(self, *args, **kwargs)
        self.send_strategy = _AmazonSESSend(self, *args, **kwargs)

    def validate_addr(self, address):
        return self.validation_strategy.validate_addr(address)

    def is_validated_addr(self, address):
        return self.validation_strategy.is_validated_addr(address)

    def check_addr_validation_status(self, *addresses):
        return self.validation_strategy.check_addr_validation_status(
            *addresses
        )

    def send(self, src, to, **kwargs):
        return self.send_strategy.send(src, to, **kwargs)


class _AmazonSESValidation(_BaseAmazonSES):
    def __init__(self, parent_strategy, *args, **kwargs):
        self._parent_strategy = parent_strategy
        super().__init__(*args, **kwargs)

    def is_validated_addr(self, address):
        validation_status = self.check_addr_validation_status(address)[address]
        return self.is_valid_addr_status(validation_status)

    def is_valid_addr_status(self, status):
        return status.lower() == "success"

    def check_addr_validation_status(self, *addresses):
        r = self._validation_status_request(*addresses)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, "lxml")
        # Unvalidated by default
        statuses = {addr: "Unvalidated" for addr in addresses}
        for entry in soup.find_all("entry"):
            statuses[entry.key.text] = entry.verificationstatus.text

        return statuses

    def _validation_status_request(self, *addresses):
        headers = self._build_request_headers()
        params = {"Action": "GetIdentityVerificationAttributes", }
        params.update({
            "Identities.member.{}".format(i): address
            for i, address in enumerate(addresses, 1)
        })

        return requests.get(
            self._parent_strategy.api_domain, headers=headers, params=params
        )

    def validate_addr(self, address):
        headers = self._build_request_headers()
        params = {
            "Action": "VerifyEmailIdentity",
            "EmailAddress": address
        }

        return requests.get(
            self._parent_strategy.api_domain, headers=headers, params=params
        )


class _AmazonSESSend(_BaseAmazonSES):
    def __init__(self, parent_strategy, *args, **kwargs):
        self._parent_strategy = parent_strategy
        super().__init__(*args, **kwargs)

    def send(self, src, to, **kwargs):
        to = tuple(to)
        if not self._parent_strategy.premium:
            self._check_every_addr_valids(*to)

        headers = self._build_request_headers()
        params = {"Action": "SendEmail", }
        self._build_mail_headers_params(params, src, to, **kwargs)
        self._build_mail_content_params(params, **kwargs)

        return requests.get(
            self._parent_strategy.api_domain, headers=headers, params=params
        )

    def _check_every_addr_valids(self, *addresses):
        validation_statuses = (
            self._parent_strategy.check_addr_validation_status(*addresses)
        )

        is_valid_addr_status_fn = (
            self._parent_strategy.validation_strategy.is_valid_addr_status
        )
        for addr, validation_status in validation_statuses.items():
            if not is_valid_addr_status_fn(validation_status):
                raise UnvalidatedAddrError(addr)

        return True

    def _build_mail_headers_params(self, params, src, to, **kwargs):
        """
        Build mail header parameters

        Read _build_receivers_params parameters documentation

        :param src: sender address
        :type src: str or tuple
        :param to: address(es) of the recipient(s)
        :type to: str or tuple
        :param reply_to: address(es) to set as Reply-To
        :type to: str or tuple
        :param subject: mail subject
        :type subject: str
        """
        params["Source"] = src
        self._build_receivers_params(params, to=to, **kwargs)

        if "reply_to" in kwargs:
            reply_to = tuple(kwargs["reply_to"])
            for i, addr in enumerate(reply_to, 1):
                params["ReplyToAddresses.member.{}".format(i)] = addr

        params["Message.Subject.Data"] = kwargs.get("subject", "No Subject")
        return params

    def _build_receivers_params(self, params, **kwargs):
        """
        :param to: address(es) of the recipient(s)
        :type to: str or tuple
        :param cc: carbon copy
        :type cc: str or tuple
        :param bcc: blind carbon copy
        :type bcc: str or tuple
        """
        assoc_aws_param_kwargs_keys = zip(
            ("ToAddresses", "CcAddresses", "BccAddresses"),
            ("to", "cc", "bcc")
        )
        for aws_param, k in assoc_aws_param_kwargs_keys:
            addresses = kwargs.get(k, [])
            if isinstance(addresses, str):
                addresses = (addresses, )
            for i, addr in enumerate(addresses, 1):
                params["Destination.{}.member.{}".format(aws_param, i)] = addr

        return params

    def _build_mail_content_params(self, params, text="", html=None, **kwargs):
        params["Message.Body.Text.Data"] = text
        if html:
            params["Message.Body.Html.Data"] = html
        return params
