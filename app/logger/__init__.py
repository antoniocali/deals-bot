import logging
from logging import Formatter
from sys import stdout


def getLogger(name: str) -> logging.Logger:
    log = logging.Logger(name.upper(), level=logging.DEBUG)
    format = Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    ch = logging.StreamHandler(stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    return log
