
from flask_restplus import Api, Resource, fields
from mail_sender_daemon import app, APP_VERSION

api = Api(
    app, version=APP_VERSION, title="Mail Sender",
    description=(
        "Send mail through Mailgun and AmazonSES with automatic failover"
    ), default="mail", default_label="Mail namespace"
)

mail_fields = api.model("MailSender", {
    "from": fields.String(description="Sender name (address is automatic)"),
    "to": fields.List(fields.String(
        description="Receiver address", required=True
    )),
})


@api.route("/send")
class SendMail(Resource):
    @api.response(200, "Mail sent")
    @api.response(400, "Validation error")
    @api.expect(mail_fields)
    def post(self):
        pass
