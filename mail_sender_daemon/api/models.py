
from flask_restplus import fields
from . import api


mail_model = api.model("MailSender", {
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

response_common_fields = {
    "providers": fields.Nested(
        description="Attempted providers",
        model=api.model("ProviderResponse", {
            "provider": fields.String(description="Provider name"),
            "status_code": fields.Integer(description="Request status code"),
            "msg": fields.String(description="Request reason message"),
        }),
    ),
}
# if returns 200, the provider used to sent the email is added
response_ok_fields = response_common_fields.copy()
response_ok_fields.update({
    "provider_used": fields.String(description="Provider name"),
})

response_error_model = api.model(
    "MailSenderErrorResponse", response_common_fields,
)
response_ok_model = api.model(
    "MailSenderOKResponse", response_ok_fields,
)
