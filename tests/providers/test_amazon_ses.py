import datetime
import pytest
import requests_mock

from mail_sender_daemon.providers import AmazonSES
from mail_sender_daemon.exceptions import UnvalidatedAddrError


class TestAmazonSES():
    url = "http://localhost"
    api_access_key = "access_key"
    api_secret_key = "secret_key"

    @pytest.fixture()
    def prepared_api(self):
        return AmazonSES(
            self.url, False, self.api_access_key, self.api_secret_key
        )

    def test_build_signature(self, prepared_api):
        date = datetime.datetime(
            2017, 10, 15, 0, 0
        ).strftime("%a, %d %b %Y %H:%M:%S GMT")

        expected_sign = "hEmPZuISw6wxac6ajU0j71wp+vQz1PqXtu8KjDlNElw="
        assert prepared_api._build_signature(date) == expected_sign

    def test_check_addr_validation_status_on_addr(self, prepared_api):
        expected_address_status = {
            "success@email.com": "Success",
        }
        received_status = self.mock_check_addr_validation_status(
            prepared_api, expected_address_status
        )
        assert received_status == expected_address_status

    def test_check_addr_validation_status_mult_addr(self, prepared_api):
        expected_addresses_statuses = {
            "success@email.com": "Success",
            "unvalidated@email.com": "Unvalidated",
        }
        received_status = self.mock_check_addr_validation_status(
            prepared_api, expected_addresses_statuses
        )
        assert received_status == expected_addresses_statuses

    def mock_check_addr_validation_status(self, prepared_api,
                                          addresses_statuses):
        """
        Mock an AmazonSES answer and check addr validation statuses

        Return the validation status result

        :param addresses_status: {email_address: status,}
        """
        with requests_mock.Mocker() as m:
            m.register_uri(
                "GET",
                self.build_validation_url(
                    "GetIdentityVerificationAttributes",
                    *addresses_statuses.keys()
                ),
                text=self.build_validation_answer(addresses_statuses)
            )
            return prepared_api.check_addr_validation_status(
                *addresses_statuses.keys()
            )

    def build_validation_url(self, action, *addresses):
        val_url = self.url + "?Action={action}".format(action=action)

        if action == "GetIdentityVerificationAttributes":
            for i, address in enumerate(addresses, 1):
                val_url += "&Identities.member.{}={}".format(i, address)
        elif action == "VerifyEmailIdentity":
            val_url += "&EmailAddress={}".format(addresses[0])

        return val_url

    def build_validation_answer(self, addresses_status):
        """
        Mock an AmazonSES validation answer from received addresses statuses

        :param addresses_status: {email_address: status,}
        """
        answer = (
            "<GetIdentityVerificationAttributesResult>"
            "<VerificationAttributes>\n"
        )

        for a, s in addresses_status.items():
            answer += (
                "<entry>"
                "<key>{address}</key>"
                "<value>"
                "<VerificationStatus>{status}</VerificationStatus>"
                "</value></entry>\n"
            ).format(address=a, status=s)

        answer += (
            "</VerificationAttributes>\n"
            "</GetIdentityVerificationAttributesResult>"
        )
        return answer

    def test_validate_addr(self, prepared_api):
        address = "test@email.com"
        with requests_mock.Mocker() as m:
            m.register_uri(
                "GET",
                self.build_validation_url(
                    "VerifyEmailIdentity", address
                ),
                status_code=200,
            )
            response = prepared_api.validate_addr(address)

        assert response.status_code == 200

    def test_send_mail(self, monkeypatch, prepared_api):
        self.mock_sender_check_addr(monkeypatch, prepared_api)

        response = self.send_mail_with_mocked_request(
            prepared_api, "sender@email.com", "dest@email.com"
        )
        assert response.status_code == 200

    def test_send_mail_unvalidated_dest(self, monkeypatch, prepared_api):
        self.mock_sender_check_addr(monkeypatch, prepared_api, valid=False)

        with pytest.raises(UnvalidatedAddrError):
            self.send_mail_with_mocked_request(
                prepared_api, "sender@email.com", "dest@email.com"
            )

    def mock_sender_check_addr(self, monkeypatch, api, valid=True):
        """
        Mock the check_addr function of the send strategy

        If valid is True, the method will return True, otherwise an
        UnvalidatedAddrError will be raised
        """
        def callback(*args, **kwargs):
            if valid:
                return True
            else:
                raise UnvalidatedAddrError("")

        monkeypatch.setattr(
            api.send_strategy, "_check_every_addr_valids", callback
        )
        return api

    def send_mail_with_mocked_request(self, prepared_api, *args, **kwargs):
        """
        *args and **kwargs will be the parameters sent to prepared_api.send()
        """
        with requests_mock.Mocker() as m:
            m.register_uri(
                "GET",
                self.url + "?Action=SendEmail",
                status_code=200,
            )
            return prepared_api.send(*args, **kwargs)
