
import os
import sys
from flask import Flask

APP_NAME = "mail-sender-daemon"
APP_VERSION = "0.0.1"

app = Flask(APP_NAME)
from mail_sender_daemon.config import build_app_config
try:
    app.config.from_mapping(
        **build_app_config(os.environ.get("CONFIG_FILE", None))
    )
except FileNotFoundError:
    sys.exit(1)

from mail_sender_daemon import api
