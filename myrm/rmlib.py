import errno
import logging
import os
import sys

# Create a new instance of the preferred reporting system for this program.
logger = logging.getLogger("myrm")


__all__ = (
    "mkdir",
    "rm",
    "rmdir",
    "mv",
    "mvdir",
)


def mkdir(path: str, dry_run: bool = False) -> None:
    try:
        if not dry_run:
            os.makedirs(path)
        logger.info("Directory '%s' was created.", path)
    except OSError as err:
        if not (err.errno == errno.EEXIST and os.path.isdir(path)):
            logger.error("Could not create the determined directory.")
            logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EPERM))


def rm(path: str, dry_run: bool = False) -> None:
    try:
        if not dry_run or not os.path.exists(path):
            os.remove(path)
        logger.info("Item '%s' was deleted from the current machine.", path)
    except OSError as err:
        logger.error("Item's path can not be deleted from the current machine.")
        logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EPERM))


def rmdir(path: str, dry_run: bool = False) -> None:
    try:
        content = os.walk(path, topdown=False)
    except OSError as err:
        logger.error("The determined path not exists on the current machine.")
        logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EPERM))

    for top, dirs, nondirs in content:
        # Step -- 1.
        for name in nondirs:
            rm(os.path.join(top, name), dry_run)

        try:
            # Step -- 2.
            for name in dirs:
                abspath = os.path.join(top, name)
                if not dry_run:
                    os.rmdir(abspath)
                logger.info("Folder '%s' was deleted from the current machine.", abspath)
        except OSError as err:
            logger.error("The determined path can't be deleted from the current machine.")
            logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EPERM))

    try:
        if not dry_run or not os.path.exists(path):
            os.rmdir(path)
    except OSError as err:
        logger.error("The determined path can't be deleted from the current machine.")
        logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EPERM))
    else:
        logger.info("Directory '%s' was deleted from the current machine.", path)


def mv(src: str, dst: str, dry_run: bool = False) -> None:
    try:
        if not dry_run or not os.path.exists(src):
            os.rename(src, dst)
        logger.info("Item '%s' was moved to '%s' as a destinational path.", src, dst)
    except OSError as err:
        logger.error("The determined item can't be moved to the destinational path.")
        logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EPERM))


def mvdir(src: str, dst: str, dry_run: bool = False) -> None:
    try:
        content = os.walk(src, topdown=False)
    except OSError as err:
        logger.error("The determined path not exists on the current machine.")
        logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
        # Stop this program runtime and return the exit status code.
        sys.exit(getattr(err, "errno", errno.EPERM))

    if not dry_run:
        for top, _, nondirs in content:
            abspath = top.replace(src, dst)

            # Step -- 1.
            mkdir(abspath, dry_run)

            # Step -- 2.
            for name in nondirs:
                mv(os.path.join(top, name), os.path.join(abspath, name), dry_run)
        rmdir(src, dry_run)
    logger.info("Directory '%s' was moved to '%s' as a destinational path.", src, dst)
