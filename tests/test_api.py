from flask import url_for
import json
import pytest

from mail_sender_daemon.providers import AmazonSES, Mailgun


class TestAPI():
    def test_send(self, monkeypatch, mocker, client):
        ok_resp = self.build_200_response(mocker)
        self.mock_sending_for_provider(monkeypatch, AmazonSES, ok_resp)
        self.mock_sending_for_provider(monkeypatch, Mailgun, ok_resp)

        resp = self.post_send(client)

        assert resp.status_code == 200
        assert len(resp.json["providers"]) == 1

    def test_send_failover(self, monkeypatch, mocker, client):
        magic_mocker_resp = self.build_503_then_200_resp(mocker)
        self.mock_sending_for_provider(
            monkeypatch, AmazonSES, magic_mocker_resp
        )
        self.mock_sending_for_provider(
            monkeypatch, Mailgun, magic_mocker_resp
        )

        resp = self.post_send(client)

        assert resp.status_code == 200
        assert len(resp.json["providers"]) == 2

    def test_send_complete_failure(self, monkeypatch, mocker, client):
        err_resp = self.build_503_response(mocker)
        self.mock_sending_for_provider(monkeypatch, AmazonSES, err_resp)
        self.mock_sending_for_provider(monkeypatch, Mailgun, err_resp)

        resp = self.post_send(client)

        assert resp.status_code == 503
        assert len(resp.json["providers"]) == 2

    def mock_sending_for_provider(self, monkeypatch, provider_class, response):
        def callback(*args, **kwargs):
            return response

        monkeypatch.setattr(provider_class, "send", callback)

    def post_send(self, client):
        return client.post(
            "/send",
            data=json.dumps({
                "from": "from@email.com",
                "to": ["to@email.com", ],
            }),
            follow_redirects=True,
            headers={
                "Content-type": "application/json",
                "Accept": "application/json"
            }
        )

    def test_check_validation(self, monkeypatch, mocker, client):
        address = "test@email.com"
        self.mock_check_validation_for_provider(
            monkeypatch, AmazonSES, {address: "Success"}
        )

        resp = client.get(url_for("validation", address=address))

        assert resp.status_code == 200
        assert resp.json["providers"][0]["validation"] == "Success"

    def test_validate(self, monkeypatch, mocker, client):
        self.mock_validation_for_provider(
            monkeypatch, AmazonSES, self.build_200_response(mocker)
        )

        assert self.post_validate(client).status_code == 200

    def test_validate_error(self, monkeypatch, mocker, client):
        self.mock_validation_for_provider(
            monkeypatch, AmazonSES, self.build_503_response(mocker)
        )

        assert self.post_validate(client).status_code == 503

    def post_validate(self, client):
        address = "test@email.com"
        return client.post(url_for("validation", address=address))

    def mock_check_validation_for_provider(self, monkeypatch, provider_class,
                                           validation_status):
        def callback(*args, **kwargs):
            return validation_status

        monkeypatch.setattr(
            provider_class, "check_addr_validation_status", callback
        )

    def mock_validation_for_provider(self, monkeypatch, provider_class,
                                     response):
        def callback(*args, **kwargs):
            return response

        monkeypatch.setattr(
            provider_class, "validate_addr", callback
        )

    def build_200_response(self, mocker):
        resp = mocker.stub()
        resp.status_code = 200
        resp.reason = "OK"
        resp.ok = True
        resp.content = ""

        return resp

    def build_503_response(self, mocker):
        resp = mocker.stub()
        resp.status_code = 503
        resp.reason = "Service Unavailable"
        resp.ok = False
        resp.content = ""

        return resp

    def build_503_then_200_resp(self, mocker):
        resp = mocker.MagicMock()
        type(resp).status_code = mocker.PropertyMock(side_effect=[503, 200])
        type(resp).reason = mocker.PropertyMock(
            side_effect=["Service Unavailable", "OK"]
        )
        type(resp).ok = mocker.PropertyMock(side_effect=[False, True])
        resp.content = ""

        return resp
