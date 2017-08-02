
from flask_restplus import fields
from . import api


mail_model = api.model("MailSender", {
    "from": fields.String(
        description=(
            "Sender name (address is automatically generated depending on the "
            "provider)"
        )
    ),
    "to": fields.List(
        fields.String(), required=True, description="Receivers addresses"
    ),
    "cc": fields.List(fields.String(), description="Carbon Copy addresses"),
    "bcc": fields.List(
        fields.String(), description="Blind Carbon Copy addresses"
    ),
    "reply_to": fields.List(
        fields.String(), description="Reply-To addresses"
    ),
    "subject": fields.String(description="Mail subject"),
    "text": fields.String(description="Mail content, as text"),
    "html": fields.String(description="Mail content, as html"),
})

status_by_provider_fields = {
    "providers": fields.List(fields.Nested(
        description="Attempted providers",
        model=api.model("StatusByProvider", {
            "provider": fields.String(description="Provider name"),
            "status_code": fields.Integer(description="Request status code"),
            "msg": fields.String(description="Request reason message"),
        }),
    )),
}
# if returns 200, the provider used to sent the email is added
send_ok_fields = status_by_provider_fields.copy()
send_ok_fields.update({
    "provider_used": fields.String(description="Provider name"),
})

validation_status_by_provider_fields = {
    "address": fields.String(description="Email address"),
    "providers": fields.List(fields.Nested(
        description="Provider",
        model=api.model("ProviderValidation", {
            "provider": fields.String(description="Provider name"),
            "validation": fields.String(
                description="Validation status"
            ),
        }),
    )),
}


status_by_provider_model = api.model(
    "StatusByProviderResponse", status_by_provider_fields,
)

send_error_model = status_by_provider_model
send_ok_model = api.model(
    "MailSenderOKResponse", send_ok_fields,
)

send_error_model = api.model(
    "MailSenderErrorResponse", status_by_provider_fields,
)

validation_status_ok_model = api.model(
    "ValidationStatusResponse", validation_status_by_provider_fields,
)
validation_error_model = status_by_provider_model
