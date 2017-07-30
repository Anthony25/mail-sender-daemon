
class MailNotSentError(Exception):
    """
    Mail not sent
    """
    def __init__(self):
        super().__init__("mail cannot be sent")
