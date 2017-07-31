
from flask_restplus import Api

from mail_sender_daemon import app, APP_VERSION

__all__ = ("api")


api = Api(
    app, version=APP_VERSION, title="Mail Sender",
    description=(
        "Send mail through Mailgun and AmazonSES with automatic failover"
    ), default="mail", default_label="Mail namespace"
)

from . import routes
