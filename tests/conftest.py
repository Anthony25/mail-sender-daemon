import pytest

import mail_sender_daemon


@pytest.fixture(scope='session')
def app(request):
    """
    Session-wide test `Flask` application.
    """
    app = mail_sender_daemon.app
    app.config["AMAZON_API_DOMAIN"] = "http://localhost/amazon/"
    app.config["MAILGUN_API_BASE_URL"] = "http://localhost/mailgun/"
    app.config["TESTING"] = True

    return app
