
import base64
import datetime
import hashlib
import hmac
import requests


class AmazonSES():
    def __init__(self, api_access_key, api_secret_key, api_domain):
        self._api_access_key = api_access_key
        self._api_secret_key = api_secret_key
        self.api_domain = api_domain

    def send(self, src, to, **kwargs):
        headers = self._build_request_headers()
        params = {"Action": "SendEmail", }
        self._build_headers_params(params, src, to, **kwargs)
        self._build_content_params(params, **kwargs)

        return requests.get(self.api_domain, headers=headers, params=params)

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

    def _build_headers_params(self, params, src, to, **kwargs):
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

    def _build_content_params(self, params, text="", html=None, **kwargs):
        params["Message.Body.Text.Data"] = text
        if html:
            params["Message.Body.Html.Data"] = html
        return params
