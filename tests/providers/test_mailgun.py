import pytest
import requests_mock

from mail_sender_daemon.providers import Mailgun


class TestMailgun():
    url = "http://localhost"
    api_key = "api_key"

    @pytest.fixture()
    def prepared_api(self):
        return Mailgun(self.api_key, self.url)

    def test_send_mail(self, prepared_api):
        response = self.send_mail_with_mocked_request(
            prepared_api, "sender@email.com", "dest@email.com"
        )
        assert response.status_code == 200

    def send_mail_with_mocked_request(self, prepared_api, *args, **kwargs):
        """
        *args and **kwargs will be the parameters sent to prepared_api.send()
        """
        with requests_mock.Mocker() as m:
            m.register_uri(
                "POST",
                self.url.rstrip("/") + "/messages",
                status_code=200,
            )
            return prepared_api.send(*args, **kwargs)
