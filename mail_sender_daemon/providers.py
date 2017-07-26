
import urllib.parse
import requests


class Mailgun():
    def __init__(self, api_key, api_base_url):
        self.api_key = api_key
        self.api_base_url = api_base_url

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
        return urllib.parse.urljoin(self.api_base_url, "messages")

    def _build_headers_params(self, params, src, to, **kwargs):
        params["from"] = src
        self._build_receivers_params(params, to=to, **kwargs)

        if "reply-to" in kwargs:
            params["h:Reply-To"] = kwargs["reply-to"]
        if "subject" in kwargs:
            params["subject"] = kwargs["subject"]

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

    def _build_content_params(self, params, text=None, html=None, **kwargs):
        if text:
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
