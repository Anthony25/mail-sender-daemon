
import logging
import os
import yaml
import appdirs

from mail_sender_daemon import app, APP_NAME

logger = logging.getLogger(APP_NAME)


os.environ["XDG_CONFIG_DIRS"] = "/etc"

CONFIG_DIRS = (
    appdirs.user_config_dir(APP_NAME),
    appdirs.site_config_dir(APP_NAME),
    os.path.abspath(os.path.join(app.root_path, "../")),
)
CONFIG_FILENAME = "config.yml"


def build_app_config(custom_path=None):
    """
    Get config file and load it with yaml

    :returns: loaded config in yaml, as a dict object
    """
    if custom_path:
        config_path = custom_path
    else:
        for d in CONFIG_DIRS:
            config_path = os.path.join(d, CONFIG_FILENAME)
            if os.path.isfile(config_path):
                break
    try:
        with open(config_path, "r") as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError as e:
        logger.debug(e)
        if custom_path:
            logger.error(
                "Configuration file {} not found.".format(custom_path)
            )
        else:
            logger.error(
                "No configuration file can be found.\n"
                "Please create a config.yml in one of these directories:\n"
                "\t{}".format("\n\t".join(CONFIG_DIRS))
            )
        raise
