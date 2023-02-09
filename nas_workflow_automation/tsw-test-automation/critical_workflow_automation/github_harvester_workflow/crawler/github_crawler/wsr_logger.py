import logging
from logging import handlers


def setup_logging(logger, level):
    logger.setLevel(level)
    # Output to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s\t[%(name)s] %(message)s'))
    logger.addHandler(console_handler)

    # Also output to syslog (for Splunk)
#    syslog_handler = handlers.SysLogHandler(address='/dev/log')
    syslog_handler = handlers.SysLogHandler()
    syslog_handler.setFormatter(logging.Formatter('%(levelname)s [%(name)s] %(message)s'))
    logger.addHandler(syslog_handler)


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    setup_logging(logger, level)
    return logger
