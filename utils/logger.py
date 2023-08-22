import logging.config
import sys

def logger(name: str) -> logging.Logger:
    LOGGING_CONFIG = {
        "version": 1,
        "formatters": {
            "standart": {"format": "%(asctime)s - %(levelname)s - %(message)s"},
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "formatter": "standart",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            name: {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(name)
    return logger
    