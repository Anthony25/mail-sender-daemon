
from flask import request
from flask_restplus import Api, Resource, fields

from mail_sender_daemon import app, APP_VERSION, APP_NAME
from mail_sender_daemon.providers import Mailgun, AmazonSES
from mail_sender_daemon.exceptions import MailNotSentError

api = Api(
    app, version=APP_VERSION, title="Mail Sender",
    description=(
        "Send mail through Mailgun and AmazonSES with automatic failover"
    ), default="mail", default_label="Mail namespace"
)

mail_fields = api.model("MailSender", {
    "from": fields.String(description="Sender name (address is automatic)"),
    "to": fields.List(
        fields.String(description="Receiver address"), required=True
    ),
    "cc": fields.List(
        fields.String(description="Carbon Copy address")
    ),
    "bcc": fields.List(
        fields.String(description="Blind Carbon Copy address")
    ),
    "reply_to": fields.List(
        fields.String(description="Reply-To address")
    ),
    "subject": fields.String(description="Mail subject"),
    "text": fields.String(description="Mail content, as text"),
    "html": fields.String(description="Mail content, as html"),
})


mail_providers = {
    "amazon_ses": AmazonSES(
        api_access_key=app.config["AMAZON_API_ACCESS_KEY"],
        api_secret_key=app.config["AMAZON_API_SECRET_KEY"],
        api_domain=app.config["AMAZON_API_DOMAIN"],
    ),
    "mailgun": Mailgun(
        api_key=app.config["MAILGUN_API_KEY"],
        api_base_url=app.config["MAILGUN_API_BASE_URL"],
    ),
}


@api.route("/send")
class SendMail(Resource):
    @api.response(200, "Mail sent")
    @api.response(400, "Validation error")
    @api.expect(mail_fields, validate=True)
    def post(self):
        mail_params = request.json
        try:
            src_name = mail_params.pop("from")
        except KeyError:
            src_name = None

        resp_by_provider = []
        try:
            # Cannot be built through a comprehensive list, as providers
            # responses have to be kept even when a mail cannot be sent
            for response in self._send_with_failover(mail_params, src_name):
                resp_by_provider.append({
                    "provider": response[0],
                    "status_code": response[1],
                    "msg":  response[2],
                })
            status = 200
        except MailNotSentError as e:
            app.logger.error("Error sending mail: {}".format(resp_by_provider))
            status = 503
        return resp_by_provider, status

    def _send_with_failover(self, mail_params, src_name=None):
        for provider, sender in mail_providers.items():
            try:
                src = self._get_sender_for_provider(provider, src_name)
                response = sender.send(src=src, **mail_params)
                app.logger.debug(
                    "{} response: {}".format(provider, response.content)
                )

                yield provider, response.status_code, response.reason
                if response.ok:
                    return
            except Exception as e:
                app.logger.error("Error sending mail to {}".format(
                    mail_params["to"]
                ), exc_info=e)
                yield provider, 500, "Internal Server Error"

        raise MailNotSentError()

    def _get_sender_for_provider(self, provider, src_name=None):
        return "{} <{}>".format(
            APP_NAME.title() if src_name is None else src_name,
            app.config["SEND_FROM"][provider]
        )
