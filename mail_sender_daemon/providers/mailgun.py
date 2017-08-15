
import requests
from . import _BaseProvider


class Mailgun(_BaseProvider):
    def __init__(self, api_key, api_base_url, *args, **kwargs):
        self.api_key = api_key
        self.api_base_url = api_base_url
        super().__init__(*args, **kwargs)

    def send(self, src, to, **kwargs):
        send_url = self.get_send_url()
        auth = requests.auth.HTTPBasicAuth("api", self.api_key)

        params = {}
        self._build_headers_params(params, src, to, **kwargs)
        self._build_content_params(params, **kwargs)
        files = {}
        self._list_attachments_files(files, **kwargs)

        return requests.post(send_url, auth=auth, data=params, files=files)

    def get_send_url(self):
        return "{}/{}".format(self.api_base_url.rstrip("/"), "messages")

    def _build_headers_params(self, params, src, to, **kwargs):
        params["from"] = src
        self._build_receivers_params(params, to=to, **kwargs)

        reply_to = kwargs.get("reply_to", None)
        if reply_to:
            if isinstance(reply_to, str):
                 reply_to = tuple(reply_to)
            params["h:Reply-To"] = ",".join(reply_to)

        params["subject"] = kwargs.get("subject", "No Subject")

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
        for k in ("to", "cc", "bcc"):
            targets = kwargs.get(k, None)
            if isinstance(targets, str):
                params[k] = targets
            elif targets:
                params[k] = ",".join(targets)

        return params

    def _build_content_params(self, params, text="", html=None, **kwargs):
        params["text"] = text
        if html:
            params["html"] = html
        return params

    def _list_attachments_files(self, files, attachment=None, inline=None,
                                **kwargs):
        if attachment:
            files["attachment"] = attachment
        if inline:
            files["inline"] = inline
        return files
