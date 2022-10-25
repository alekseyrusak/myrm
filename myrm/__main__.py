import argparse
import errno
import logging
import os
import sys
from typing import Any

from . import __version__, bucket, settings

logger = logging.getLogger("myrm")


def abspath(path: str) -> str:
    """
    The function converts the user-entered path to an absolute path.
    """
    dirname = os.path.dirname(os.path.abspath(__file__))

    return os.path.normpath(os.path.join(dirname, path))


def restore(arguments: Any, trash_bin: Any) -> None:
    for index in arguments.INDICES:
        trash_bin.restore(index)


def show(arguments: Any, trash_bin: Any) -> None:
    print(trash_bin.history.get_table(page=arguments.page, count=arguments.limit))


def remove(arguments: Any, trash_bin: Any) -> None:
    for item in arguments.FILES:
        trash_bin.rm(item, force=arguments.force)


def maintain(arguments: Any, trash_bin: Any) -> None:
    if arguments.create:
        trash_bin.create()

    if arguments.cleanup:
        trash_bin.cleanup()


class SettingsArgumentsWrapper:
    app_settings: settings.AppSettings = settings.AppSettings()

    def __call__(self, arguments: Any) -> settings.AppSettings:
        # Step -- 1.
        self.app_settings = settings.load(arguments.settings)

        # Step -- 2.
        for name, value in (
            ("bucket_path", settings.DEFAULT_BUCKET_PATH),
            ("bucket_history_path", settings.DEFAULT_BUCKET_HISTORY_PATH),
            ("bucket_size", settings.DEFAULT_BUCKET_SIZE),
            ("bucket_storetime", settings.DEFAULT_CLEANUP_TIME),
        ):
            if getattr(arguments, name) == value:
                continue
            setattr(self.app_settings, name, getattr(arguments, name))

        return self.app_settings


def main() -> None:
    # Step -- 1.
    settings_parser = argparse.ArgumentParser(add_help=False)
    settings_parser.add_argument(
        "--settings",
        type=abspath,
        default=settings.DEFAULT_SETTINGS_PATH,
        help="the absolutly path where settings file will be store on the curent machine",
    )
    settings_parser.add_argument(
        "--bucket-path",
        type=abspath,
        default=settings.DEFAULT_BUCKET_PATH,
        help="the absolutly path where bucket will be store on the curent machine",
    )
    settings_parser.add_argument(
        "--bucket-history-path",
        type=abspath,
        default=settings.DEFAULT_BUCKET_HISTORY_PATH,
        help="the absolutly path where bucket history will be store on the curent machine",
    )
    settings_parser.add_argument(
        "--bucket-size",
        type=lambda size: int(size) * settings.BYTES_TO_MBYTES,
        default=settings.DEFAULT_BUCKET_SIZE,
        help="bucket's max size in megabytes",
    )
    settings_parser.add_argument(
        "--bucket-storetime",
        type=lambda time: int(time) * settings.SECONDS_TO_DAYS,
        default=settings.DEFAULT_CLEANUP_TIME,
        help="bucket's storetime time in days",
    )
    settings_parser.set_defaults(get_settings=SettingsArgumentsWrapper())

    # Step -- 2.
    logger_parser = argparse.ArgumentParser(add_help=False)
    logger_group = logger_parser.add_mutually_exclusive_group()
    logger_group.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,  # level must be an int or a str
        default=logging.INFO,
        dest="logging_level",
        help="print a lot of debugging statements while executing user's commands",
    )
    logger_group.add_argument(
        "-s",
        "--silent",
        action="store_const",
        const=logging.NOTSET,  # level must be an int or a str
        default=logging.INFO,
        dest="logging_level",
        help="do not print any statements while executing user's commands",
    )

    # Step -- 3.
    parser = argparse.ArgumentParser(add_help=True, parents=[settings_parser, logger_parser])
    parser.add_argument("-v", "--version", action="version", version=str(__version__))
    parser.add_argument(
        "--generate-settings",
        action="store_true",
        default=False,
        help="create a new settings file on the current machine",
    )

    group = parser.add_subparsers()

    # Step -- 4.
    rm_parser = group.add_parser("rm", parents=[settings_parser, logger_parser])
    rm_parser.add_argument("FILES", nargs="+", type=abspath)
    rm_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="permanently delete the determined object(s) from the current machine",
    )
    rm_parser.set_defaults(func=remove)

    # Step -- 5.
    show_parser = group.add_parser("show", parents=[settings_parser, logger_parser])
    show_parser.add_argument("--limit", default=20, type=int)
    show_parser.add_argument("--page", default=1, type=int)
    show_parser.set_defaults(func=show)

    # Step -- 6
    restore_parser = group.add_parser("restore", parents=[settings_parser, logger_parser])
    restore_parser.add_argument("INDICES", nargs="+", type=int)
    restore_parser.set_defaults(func=restore)

    # Step -- 7.
    bucket_parser = group.add_parser("bucket", parents=[settings_parser, logger_parser])
    bucket_group = bucket_parser.add_mutually_exclusive_group(required=True)
    bucket_group.add_argument("--cleanup", action="store_true", default=False)
    bucket_group.add_argument("--create", action="store_true", default=False)
    bucket_parser.set_defaults(func=maintain)

    # Step -- 8.
    try:
        args = parser.parse_args()

        if args.generate_settings:
            settings.generate()
        else:
            logger.setLevel(args.logging_level)
            app_settings = args.get_settings(args)
            app_bucket = bucket.Bucket(
                path=app_settings.bucket_path,
                history_path=app_settings.bucket_history_path,
                maxsize=app_settings.bucket_size,
                storetime=app_settings.bucket_storetime,
            )
            app_bucket.startup()
            args.func(args, app_bucket)
    except KeyboardInterrupt as err:
        logger.error("Stop this program runtime on the current machine.")
        logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EINTR))


if __name__ == "__main__":
    main()
