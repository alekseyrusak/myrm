import logging
import logging.config
import os
import tempfile
import types
from typing import Any, Mapping

LOGGING_CONFIG: Mapping[str, Any] = types.MappingProxyType(
    {
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(levelname)s :: %(name)s :: %(message)s",
                # Use this string to format the creation time of the record.
                "datefmt": "%Y-%m-%d--%H-%M-%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "logfile": {
                "class": "logging.FileHandler",
                "encoding": "utf-8",
                "filename": os.path.join(tempfile.gettempdir(), "myrm.log"),
                "formatter": "default",
                "mode": "at",
            },
        },
        "loggers": {
            "myrm": {
                "handlers": ["console", "logfile"],
            },
        },
        # Set the preferred schema version.
        "version": 1,
    }
)


def setup() -> None:
    logging.config.dictConfig(config=dict(LOGGING_CONFIG))
