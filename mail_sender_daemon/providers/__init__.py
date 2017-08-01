
__all__ = ("AmazonSES", "Mailgun")


class _BaseProvider():
    def validate_addr(self, address):
        raise NotImplementedError

    def is_validated_addr(self, address):
        raise NotImplementedError

    def check_addr_validation_status(self, *addresses):
        raise NotImplementedError

    def send(self, src, to, **kwargs):
        raise NotImplementedError


from .amazon_ses import AmazonSES
from .mailgun import Mailgun
