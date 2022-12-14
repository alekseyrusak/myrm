import collections
import enum
import errno
import io
import logging
import os
import pickle
import sys
import time
import uuid
from typing import Any, Hashable, List

from prettytable import PrettyTable

from . import rmlib, settings

# Create a new instance of the preferred reporting system for this program.
logger = logging.getLogger("myrm")


__all__ = (
    "Bucket",
    "BucketHistory",
)


class Status(enum.Enum):
    CORRECT: str = "Correct"
    UNKNOWN: str = "Unknown"


Entry = collections.namedtuple("Entry", "status index name path date origin")


class BucketHistory(collections.UserDict):
    def __init__(
        self, *args: Any, path: str = settings.DEFAULT_BUCKET_HISTORY_PATH, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self.path = path
        # Load the history state from the provided path.
        if os.path.isfile(path):
            self._read()

    def __getitem__(self, key: Hashable) -> Entry:
        return self.data[key]

    def __setitem__(self, key: Hashable, value: Entry) -> None:
        self.data[key] = value
        self._write()

    def __delitem__(self, key: Hashable) -> None:
        del self.data[key]
        self._write()

    def _read(self) -> None:
        try:
            with io.open(self.path, mode="rb") as stream_in:
                # Load and de-serialize the required data structure.
                self.update(pickle.load(stream_in))
        except (IOError, OSError) as err:
            logger.error("It's impossible to restore the history state on the current machine.")
            logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EIO))

    def _write(self) -> None:
        try:
            with io.open(self.path, mode="wb") as stream_out:
                # Serialize the required data structure and save it on the current machine.
                pickle.dump(self.data, stream_out, protocol=pickle.HIGHEST_PROTOCOL)
        except (IOError, OSError) as err:
            logger.error("It's impossible to save the history state on the current machine.")
            logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EIO))

    def get_indices(self) -> List[int]:
        return [value.index for value in self.values()]

    def get_next_index(self) -> int:
        index = 1
        if len(self.data):
            index = max(self.get_indices()) + 1

        return index

    def cleanup(self, dry_run: bool = False) -> None:
        if not dry_run:
            self.data = {}
            self._write()

    def get_table(self, page: int = 1, count: int = 10) -> PrettyTable:
        values = list(self.values())
        if not values:
            logger.warning("Show content of the bucket failed because the main bucket is empty.")
            # Stop this program runtime and return the exit status code.
            sys.exit(errno.EPERM)

        try:
            pages = [
                values[index : index + count] for index in range(0, len(values), count)  # noqa
            ]
            # Get the required page number.
            res = [list(item)[:-1] for item in pages[page - 1]]
        except IndexError as err:
            logger.error("It's impossible to get the required page number.")
            logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EPERM))

        table = PrettyTable(
            align="l",
            field_names=[
                "Status",
                "Index",
                "Name",
                "Original location",
                "Trashed on",
            ],
        )
        table.add_rows(res)

        return table


class Bucket:
    def __init__(
        self,
        path: str = settings.DEFAULT_BUCKET_PATH,
        history_path: str = settings.DEFAULT_BUCKET_HISTORY_PATH,
        maxsize: int = settings.DEFAULT_BUCKET_SIZE,
        storetime: int = settings.DEFAULT_CLEANUP_TIME,
    ) -> None:
        self.path = path
        self.maxsize = maxsize
        self.storetime = storetime
        self.history = BucketHistory(path=history_path)

    def _rm(self, path: str, dry_run: bool = False) -> None:
        if os.path.isdir(path):
            rmlib.rmdir(path, dry_run)
        else:
            rmlib.rm(path, dry_run)

    def _mv(self, path: str, dry_run: bool = False) -> None:
        origin = os.path.basename(path)
        name = str(uuid.uuid4())
        date = time.strftime("%H:%M:%S %m-%d-%Y", time.localtime())

        index = self.history.get_next_index()

        if os.path.isdir(path):
            rmlib.mvdir(path, os.path.join(self.path, name), dry_run)
        else:
            rmlib.mv(path, os.path.join(self.path, name), dry_run)

        shorted_path = path
        if len(path) > 50:
            # Prevent the terminal stdout from longer item paths.
            shorted_path = "".join([path[0:15], " ... ", path[len(path) - 30 :]])  # noqa

        self.history[name] = Entry(Status.CORRECT.value, index, origin, shorted_path, date, path)

    def _get_size(self, path: str) -> int:
        size = 0

        if os.path.isfile(path) and not os.path.islink(path):
            try:
                return os.path.getsize(path)
            except (OSError, IOError) as err:
                logger.error("It's impossible to get the size of the determined path.")
                logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
                # Stop this program runtime and return the exit status code.
                sys.exit(getattr(err, "errno", errno.EIO))

        try:
            content = os.walk(self.path)
        except OSError as err:
            logger.error("The determined path not exists on the current machine.")
            logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EPERM))

        for top, _, nondirs in content:
            for name in nondirs:
                abspath = os.path.join(top, name)

                if not os.path.islink(abspath):
                    try:
                        size += os.path.getsize(abspath)
                    except OSError as err:
                        logger.error("The calculation size for the current item is unavailable.")
                        logger.debug(
                            "An unexpected error occurred at this program runtime:", exc_info=True
                        )
                        # Stop this program runtime and return the exit status code.
                        sys.exit(getattr(err, "errno", errno.EPERM))

        return size

    def create(self, dry_run: bool = False) -> None:
        rmlib.mkdir(self.path, dry_run)

    def startup(self) -> None:
        self.create()
        self.check_content()
        self.timeout_cleanup()
        self.check_content()

    def cleanup(self, dry_run: bool = False) -> None:
        rmlib.rmdir(self.path, dry_run)
        self.create(dry_run)
        self.history.cleanup(dry_run)

    def rm(self, path: str, force: bool = False, dry_run: bool = False) -> None:
        if self.maxsize <= self.get_size() + self._get_size(path):
            logger.error("The maximum trash bin size has been exceeded.")
            # Stop this program runtime and return the exit status code.
            sys.exit(errno.EPERM)

        if not force:
            self._mv(path, dry_run)
        elif force:
            self._rm(path, dry_run)

    def get_size(self) -> int:
        return self._get_size(self.path)

    def check_content(self) -> None:
        try:
            content = os.listdir(self.path)
        except OSError as err:
            logger.error("The determined path not exists on the current machine.")
            logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EPERM))

        for name in content:
            if os.path.islink(os.path.join(self.path, name)):
                trashed_time = time.localtime()
            else:
                trashed_time = time.localtime(os.path.getatime(os.path.join(self.path, name)))
            date = time.strftime("%H:%M:%S %m-%d-%Y", trashed_time)

            index = self.history.get_next_index()

            if name not in list(self.history):
                self.history[name] = Entry(
                    Status.UNKNOWN.value,
                    index,
                    name,
                    Status.UNKNOWN.value,
                    date,
                    Status.UNKNOWN.value,
                )

        for key in list(self.history):
            if key not in content:
                del self.history[key]

    def timeout_cleanup(self) -> None:
        current_time = time.time()
        try:
            content = os.listdir(self.path)
        except OSError as err:
            logger.error("The determined path not exists on the current machine.")
            logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
            # Stop this program runtime and return the exit status code.
            sys.exit(getattr(err, "errno", errno.EPERM))

        for name in content:
            abspath = os.path.join(self.path, name)

            try:
                trashed_time = time.mktime(
                    time.strptime(self.history[name].date, "%H:%M:%S %m-%d-%Y")
                )
            except OSError as err:
                logger.error("Can't detect trashed time for the determined path.")
                logger.debug("An unexpected error occurred at this program runtime:", exc_info=True)
                # Stop this program runtime and return the exit status code.
                sys.exit(getattr(err, "errno", errno.EPERM))

            if (current_time - trashed_time) >= self.storetime:
                self._rm(abspath)

    def restore(self, index: int, dry_run: bool = False) -> None:
        if not self.history:
            logger.error("Restore failed because the main bin is empty.")
            # Stop this program runtime and return the exit status code.
            sys.exit(errno.EPERM)

        for key in self.history.keys():  # pylint: disable=consider-using-dict-items
            if self.history[key].index == index:
                name = key
            elif index not in self.history.get_indices():
                logger.error("Restore failed because the required index '%s' was not found.", index)
                # Stop this program runtime and return the exit status code.
                sys.exit(errno.EPERM)

        if self.history[name].status == Status.UNKNOWN.value:
            logger.error("Restore failed because the original location is unknown.")
            # Stop this program runtime and return the exit status code.
            sys.exit(errno.EPERM)

        src = os.path.join(self.path, name)
        dst = self.history[name].origin
        if os.path.exists(dst):
            logger.error("Restore failed because the destination path exists.")
            # Stop this program runtime and return the exit status code.
            sys.exit(errno.EPERM)

        if os.path.isdir(src):
            rmlib.mvdir(src, dst, dry_run)
        else:
            rmlib.mv(src, dst, dry_run)

        self.check_content()
