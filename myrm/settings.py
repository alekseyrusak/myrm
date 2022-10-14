import errno
import io
import json
import logging
import os
import sys
from typing import Any

# Create a new instance of the preferred reporting system for this program.
logger = logging.getLogger("myrm")


__all__ = (
    "SECONDS_TO_DAYS",
    "BYTES_TO_MBYTES",
    "HOME",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "DEFAULT_BUCKET_PATH",
    "DEFAULT_BUCKET_HISTORY_PATH",
    "DEFAULT_BUCKET_SIZE",
    "DEFAULT_CLEANUP_TIME",
    "ValidationError",
    "AppSettings",
    "load",
)

SECONDS_TO_DAYS: int = 60 * 60 * 24
BYTES_TO_MBYTES: int = 1024 * 1024

HOME: str = os.path.expanduser("~")

# Where user-specific configurations should be written.
XDG_CONFIG_HOME: str = os.path.join(HOME, ".config", "myrm")

# Where user-specific data files should be written.
XDG_DATA_HOME: str = os.path.join(HOME, ".local", "share", "myrm")

DEFAULT_BUCKET_PATH: str = os.path.join(XDG_DATA_HOME, "trash_bin")
DEFAULT_BUCKET_HISTORY_PATH: str = os.path.join(XDG_DATA_HOME, "history.pkl")

DEFAULT_BUCKET_SIZE: int = BYTES_TO_MBYTES * 1024
DEFAULT_CLEANUP_TIME: int = SECONDS_TO_DAYS * 7


class ValidationError(ValueError):
    """This exception will occured when the validation in descriptors was not pass."""


class PathField:
    def __init__(self) -> None:
        self.path = os.path.expanduser("~")

    def __get__(self, instance: Any, owner: Any) -> str:
        return self.path

    def __set__(self, instance: Any, path: str) -> None:
        if not isinstance(path, str):
            raise ValidationError(f"Path must be string but recieved: {type(path)!r}")

        if not path:
            raise ValidationError("Path can not be empty.")

        self.path = os.path.abspath(os.path.expanduser(path))


class PositiveIntegerField:
    def __init__(self) -> None:
        self.number = 0

    def __get__(self, instance: Any, owner: Any) -> int:
        return self.number

    def __set__(self, instance: Any, number: int) -> None:
        if not isinstance(number, int):
            raise ValidationError(f"Number must be integer but recieved: {type(number)!r}.")

        if number < 0:
            raise ValidationError("Number must be positive.")

        self.number = number


class BooleanField:
    def __init__(self) -> None:
        self.flag = False

    def __get__(self, instance: Any, owner: Any) -> bool:
        return self.flag

    def __set__(self, instance: Any, flag: bool) -> None:
        if not isinstance(flag, bool):
            raise ValidationError(f"Flag must be boolean but recieved: {type(flag)!r}.")

        self.flag = flag


class AppSettings:
    bucket_path = PathField()
    bucket_history_path = PathField()
    bucket_size = PositiveIntegerField()
    bucket_cleanup_time = PositiveIntegerField()

    def __init__(
        self,
        bucket_path: str = DEFAULT_BUCKET_PATH,
        bucket_history_path: str = DEFAULT_BUCKET_HISTORY_PATH,
        bucket_size: int = DEFAULT_BUCKET_SIZE,
        bucket_cleanup_time: int = DEFAULT_CLEANUP_TIME,
    ) -> None:
        try:
            self.bucket_path = bucket_path
            self.bucket_history_path = bucket_history_path
            self.bucket_size = bucket_size
            self.bucket_cleanup_time = bucket_cleanup_time
        except ValidationError as err:
            logger.error("The validation process was failed: %s", err)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EPERM))


def load(path: str) -> AppSettings:
    try:
        with io.open(path, mode="rt", encoding="utf-8") as stream_in:
            return AppSettings(**json.load(stream_in))
    except TypeError as err:
        logger.error("It's impossible to parse the provided settings scheme.")
        logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EPERM))

    except (IOError, OSError) as err:
        logger.error("It's impossible to load the settings from the current machine.")
        logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EIO))
