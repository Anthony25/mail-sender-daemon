
class MailNotSentError(Exception):
    """
    Mail not sent
    """
    def __init__(self):
        super().__init__("mail cannot be sent")


class UnvalidatedAddrError(Exception):
    """
    Mail not sent
    """
    def __init__(self, address):
        super().__init__("address {} is not validated".format(address))
