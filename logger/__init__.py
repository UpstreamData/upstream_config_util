import logging
import os

import settings


def init_logger():
    if settings.get("log_to_file", False):
        logging.basicConfig(
            filename=os.path.join(settings.BASE_DIR, "logfile.txt"),
            filemode="a",
            format="%(pathname)s:%(lineno)d in %(funcName)s\n[%(levelname)s][%(asctime)s](%(name)s) - %(message)s",
            datefmt="%x %X",
        )
    else:
        logging.basicConfig(
            format="%(pathname)s:%(lineno)d in %(funcName)s\n[%(levelname)s][%(asctime)s](%(name)s) - %(message)s",
            datefmt="%x %X",
        )

    _logger = logging.getLogger()

    if settings.get("debug", False):
        _logger.setLevel(logging.DEBUG)
        logging.getLogger("asyncssh").setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.WARNING)
        logging.getLogger("asyncssh").setLevel(logging.WARNING)

    return _logger


logger = init_logger()
