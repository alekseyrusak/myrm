import errno
import io
import os
import pickle

import pytest
from prettytable import PrettyTable

from myrm import bucket


def test_delitem_bucket_history(fake_bucket_history):
    history = {"1": 1, "2": 2, "3": 3}
    fake_bucket_history.update(history)

    del fake_bucket_history["1"]
    del fake_bucket_history["2"]
    assert list(fake_bucket_history.values()) == [3]

    with io.open(fake_bucket_history.path, mode="rb") as stream_in:
        assert pickle.load(stream_in) == {"3": 3}


def test_read_bucket_history(fs):
    path = "test.pkl"
    history = {"1": 1, "2": 2, "3": 3}
    with io.open(path, mode="wb") as stream_out:
        pickle.dump(history, stream_out, protocol=pickle.HIGHEST_PROTOCOL)

    assert bucket.BucketHistory(path=path) == history


def test_read_bucket_history_with_error(fake_bucket_history, mocker):
    logger_mock = mocker.patch("myrm.bucket.logger")
    open_mock = mocker.patch("myrm.bucket.io.open")
    open_mock.side_effect = IOError(errno.EIO, "")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket_history._read()

    logger_mock.error.assert_called_with(
        "It's impossible to restore the history state on the current machine."
    )
    assert exit_info.value.code == errno.EIO


def test_write_bucket_history(fake_bucket_history):
    history = {"1": 1, "2": 2, "3": 3}
    fake_bucket_history.update(history)

    with io.open(fake_bucket_history.path, mode="rb") as stream_in:
        assert pickle.load(stream_in) == history


def test_write_bucket_history_with_error(fake_bucket_history, mocker):
    logger_mock = mocker.patch("myrm.bucket.logger")
    open_mock = mocker.patch("myrm.bucket.io.open")
    open_mock.side_effect = IOError(errno.EIO, "")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket_history._write()

    logger_mock.error.assert_called_with(
        "It's impossible to save the history state on the current machine."
    )
    assert exit_info.value.code == errno.EIO


def test_get_indices_bucket_history(fake_bucket_history, fake_entry):
    fake_bucket_history["test"] = fake_entry
    assert fake_bucket_history.get_indices() == [1]


def test_get_next_index_bucket_history(fake_bucket_history, fake_entry):
    fake_bucket_history["test"] = fake_entry
    assert fake_bucket_history.get_next_index() == 2


def test_bucket_history_cleanup(fake_bucket_history, fake_entry):
    fake_bucket_history["test"] = fake_entry
    fake_bucket_history.cleanup(dry_run=False)

    with io.open(fake_bucket_history.path, mode="rb") as stream_in:
        assert pickle.load(stream_in) == {}
    assert not len(fake_bucket_history)


def test_bucket_history_cleanup_with_dry_run(fake_bucket_history, fake_entry):
    fake_bucket_history["test"] = fake_entry
    fake_bucket_history.cleanup(dry_run=True)

    with io.open(fake_bucket_history.path, mode="rb") as stream_in:
        assert pickle.load(stream_in) == fake_bucket_history
    assert fake_bucket_history["test"] == fake_entry


def test_get_table_bucket_history(fake_bucket_history, fake_entry):
    fake_bucket_history["test"] = fake_entry
    table = fake_bucket_history.get_table()

    assert table is not None and isinstance(table, PrettyTable)


def test_get_table_bucket_history_with_warning(fake_bucket_history, mocker):
    logger_mock = mocker.patch("myrm.bucket.logger")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket_history.get_table(1, 1)

    logger_mock.warning.assert_called_with(
        "Show content of the bucket failed because tha main bucket is empty."
    )
    assert exit_info.value.code == errno.EPERM


def test_get_table_bucket_history_with_index_error(fake_bucket_history, fake_entry, mocker):
    fake_bucket_history["test"] = fake_entry

    logger_mock = mocker.patch("myrm.bucket.logger")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket_history.get_table(13, 2)

    logger_mock.error.assert_called_with("It's impossible to get the required page number.")
    assert exit_info.value.code == errno.EPERM


def test_bucket_permanent_rm_file(fake_bucket, fs):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket._rm(path, dry_run=False)
    assert not os.path.exists(path)


def test_bucket_permanent_rm_file_with_dry_run(fake_bucket, fs):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket._rm(path, dry_run=True)
    assert os.path.exists(path) and os.path.isfile(path)


def test_bucket_permanent_rm_folder(fake_bucket, fs):
    path = "test"
    fs.create_dir(path)

    fake_bucket._rm(path, dry_run=False)
    assert not os.path.exists(path)


def test_bucket_permanent_rm_folder_with_dry_run(fake_bucket, fs):
    path = "test"
    fs.create_dir(path)

    fake_bucket._rm(path, dry_run=True)
    assert os.path.exists(path) and os.path.isdir(path)


def test_bucket_mv_file(fs, fake_bucket):
    path = "test_file_looooooooooooooooooooooooong_nameeeeeeeeeeeeeeeeee.txt"
    fs.create_file(path)

    fake_bucket._mv(path, dry_run=False)
    assert not os.path.exists(path) and len(os.listdir(fake_bucket.path))
    assert len(list(fake_bucket.history.values())[0].path) <= 50


def test_bucket_mv_file_with_dry_run(fs, fake_bucket):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket._mv(path, dry_run=True)
    assert os.path.exists(path) and not len(os.listdir(fake_bucket.path))


def test_bucket_mv_folder(fs, fake_bucket):
    path = "test"
    fs.create_dir(path)

    fake_bucket._mv(path, dry_run=False)
    assert not os.path.exists(path) and len(os.listdir(fake_bucket.path))


def test_bucket_mv_folder_with_dry_run(fs, fake_bucket):
    path = "test"
    fs.create_dir(path)

    fake_bucket._mv(path, dry_run=True)
    assert os.path.exists(path) and not len(os.listdir(fake_bucket.path))


def test_create_bucket(fs):
    test_bucket = bucket.Bucket(path="test")

    assert not os.path.exists(test_bucket.path)
    test_bucket.create(dry_run=False)
    assert os.path.isdir(test_bucket.path)


def test_create_bucket_with_dry_run():
    test_bucket = bucket.Bucket(path="test")

    test_bucket.create(dry_run=True)
    assert not os.path.exists(test_bucket.path)


def test_startup_bucket(fs):
    test_bucket = bucket.Bucket(path="trash", history_path="history.pkl")
    test_bucket.startup()

    assert os.path.exists(test_bucket.path)
    assert os.listdir(test_bucket.path) == list(test_bucket.history.keys())


def test_cleanup_bucket(fake_bucket):
    fake_bucket.cleanup(dry_run=False)
    assert os.path.exists(fake_bucket.path) and not len(os.listdir(fake_bucket.path))
    assert fake_bucket.history == {}


def test_cleanup_bucket_with_dry_run(fake_bucket, fake_bucket_history, fake_entry, fs):
    path = os.path.join(fake_bucket.path, "test.txt")
    fs.create_file(path)

    fake_bucket_history["test"] = fake_entry

    fake_bucket.cleanup(dry_run=True)

    with io.open(fake_bucket_history.path, mode="rb") as stream_in:
        assert pickle.load(stream_in) == fake_bucket_history
    assert fake_bucket_history["test"] == fake_entry
    assert os.path.exists(path)


def test_rm_to_bucket_force(fs, fake_bucket):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket.rm(path, force=True, dry_run=False)
    assert not os.path.exists(path)


def test_rm_to_bucket_force_with_dry_run(fs, fake_bucket):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket.rm(path, force=True, dry_run=True)
    assert os.path.exists(path)


def test_rm_to_bucket_not_force(fs, fake_bucket):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket.rm(path, force=False, dry_run=False)
    assert not os.path.exists(path) and len(os.listdir(fake_bucket.path))


def test_rm_to_bucket_not_force_with_dry_run(fs, fake_bucket):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket.rm(path, force=False, dry_run=True)
    assert os.path.exists(path) and not len(os.listdir(fake_bucket.path))


def test_rm_to_bucket_with_maxsize_error(fake_bucket, mocker):
    fake_bucket.maxsize = 0

    mocker.patch("myrm.bucket.os.path.getsize", return_value=10)
    logger_mock = mocker.patch("myrm.bucket.logger")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket.rm("", force=False, dry_run=False)

    logger_mock.error.assert_called_with("Maximum trash bin size exided.")
    assert exit_info.value.code == errno.EPERM


def test_get_size_bucket(fake_bucket, fs):
    path = "test.txt"
    fs.create_file(path, contents="test")

    fake_bucket.rm(path, force=False, dry_run=False)
    assert fake_bucket.get_size() > 0


def test_get_size_with_not_impossible_error(fake_bucket, mocker):
    logger_mock = mocker.patch("myrm.bucket.logger")
    get_size_mock = mocker.patch("os.path.getsize")
    get_size_mock.side_effect = IOError(errno.EIO, "")

    mocker.patch("myrm.bucket.os.path.isfile", return_value=True)
    mocker.patch("myrm.bucket.os.path.islink", return_value=False)

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket._get_size("test.txt")

    logger_mock.error.assert_called_with("It's impossible to get size of the determined path.")
    assert exit_info.value.code == errno.EIO


def test_get_size_bucket_with_not_exists_error(mocker):
    test_bucket = bucket.Bucket("")

    logger_mock = mocker.patch("myrm.bucket.logger")
    walk_mock = mocker.patch("myrm.bucket.os.walk")
    walk_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        test_bucket.get_size()

    logger_mock.error.assert_called_with("The determined path not exists on the current machine.")
    assert exit_info.value.code == errno.EPERM


def test_get_size_bucket_with_abspath_error(fake_bucket, fs, mocker):
    fs.create_file(os.path.join(fake_bucket.path, "test.txt"))
    logger_mock = mocker.patch("myrm.bucket.logger")
    getsize_mock = mocker.patch("myrm.bucket.os.path.getsize")
    getsize_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket.get_size()

    logger_mock.error.assert_called_with("The calculation size for the current item unavailable.")
    assert exit_info.value.code == errno.EPERM


def test_check_content_bucket(fake_bucket, fs):
    path = "test.txt"
    fs.create_file(os.path.join(fake_bucket.path, path))

    fake_bucket.check_content()
    assert len(os.listdir(fake_bucket.path))
    assert path == list(fake_bucket.history.values())[0].name


def test_check_content_bucket_if_islink(fake_bucket, fs, mocker):
    src = "test"
    fs.create_file(src)
    path = "test_link"
    fs.create_symlink(os.path.join(fake_bucket.path, path), "file")
    mocker.patch("myrm.bucket.os.path.islink", return_value=True)

    fake_bucket.check_content()
    assert len(os.listdir(fake_bucket.path))
    assert path == list(fake_bucket.history.values())[0].name


def test_check_content_bucket_history(fake_bucket, fake_entry):
    path = "test.txt"
    fake_bucket.history[path] = fake_entry

    fake_bucket.check_content()
    assert path not in fake_bucket.history


def test_check_content_bucket_with_not_exists_error(mocker):
    test_bucket = bucket.Bucket("")

    logger_mock = mocker.patch("myrm.bucket.logger")
    listdir_mock = mocker.patch("myrm.bucket.os.listdir")
    listdir_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        test_bucket.check_content()

    logger_mock.error.assert_called_with("The determined path not exists on the current machine.")
    assert exit_info.value.code == errno.EPERM


def test_timeout_cleanup_bucket(fake_bucket, fs, mocker):
    fs.create_file(os.path.join(fake_bucket.path, "test.txt"))
    before_cleanup_content = os.listdir(fake_bucket.path)

    fake_bucket.storetime = 1
    mocker.patch("myrm.settings.SECONDS_TO_DAYS", new=1)
    mocker.patch("myrm.bucket.time.mktime", return_value=1)
    mocker.patch("myrm.bucket.time.time", return_value=10)

    fake_bucket.check_content()
    fake_bucket.timeout_cleanup()
    assert before_cleanup_content != os.listdir(fake_bucket.path)


def test_timeout_cleanup_bucket_with_not_exists_error(mocker):
    test_bucket = bucket.Bucket("")

    logger_mock = mocker.patch("myrm.bucket.logger")
    listdir_mock = mocker.patch("myrm.bucket.os.listdir")
    listdir_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        test_bucket.timeout_cleanup()

    logger_mock.error.assert_called_with("The determined path not exists on the current machine.")
    assert exit_info.value.code == errno.EPERM


def test_timeout_cleanup_bucket_with_trashed_time_error(fake_bucket, fs, mocker):
    fs.create_file(os.path.join(fake_bucket.path, "test.txt"))

    logger_mock = mocker.patch("myrm.bucket.logger")
    gettime_mock = mocker.patch("myrm.bucket.time.mktime")
    gettime_mock.side_effect = OSError(errno.EPERM, "")

    fake_bucket.check_content()

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket.timeout_cleanup()

    logger_mock.error.assert_called_with("Can't detect trashed time for the determined path.")
    assert exit_info.value.code == errno.EPERM


def test_restore_file_from_bucket(fake_bucket, fs):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket.rm(path, force=False, dry_run=False)
    before_restore_path = os.path.exists(path)

    fake_bucket.restore(1, dry_run=False)
    assert os.path.exists(path) and not before_restore_path


def test_restore_file_from_bucket_with_dry_run(fake_bucket, fs):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket.rm(path, force=False, dry_run=False)

    fake_bucket.restore(1, dry_run=True)
    assert not os.path.exists(path) and len(os.listdir(fake_bucket.path))


def test_restore_folder_from_bucket(fake_bucket, fs):
    path = "test"
    fs.create_dir(path)

    fake_bucket.rm(path, force=False, dry_run=False)
    before_restore_path = os.path.exists(path)

    fake_bucket.restore(1, dry_run=False)
    assert os.path.exists(path) and not before_restore_path


def test_restore_folder_from_bucket_with_dry_run(fake_bucket, fs):
    path = "test"
    fs.create_dir(path)

    fake_bucket.rm(path, force=False, dry_run=False)

    fake_bucket.restore(1, dry_run=True)
    assert not os.path.exists(path) and len(os.listdir(fake_bucket.path))


def test_restore_with_bucket_is_empty_error(fake_bucket, mocker):
    logger_mock = mocker.patch("myrm.bucket.logger")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket.restore(5, dry_run=False)

    logger_mock.error.assert_called_with("Restore failed because tha main bin is empty.")
    assert exit_info.value.code == errno.EPERM


def test_restore_with_index_error(fake_bucket, fake_entry, mocker):
    fake_bucket.history["test"] = fake_entry
    index = 99

    logger_mock = mocker.patch("myrm.bucket.logger")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket.restore(index, dry_run=False)

    logger_mock.error.assert_called_with(
        "Restore failed because the required index '%s' not found.", index
    )
    assert exit_info.value.code == errno.EPERM


def test_restore_with_status_unknown_error(fake_bucket, fs, mocker):
    logger_mock = mocker.patch("myrm.bucket.logger")

    fs.create_file(os.path.join(fake_bucket.path, "test.txt"))
    fake_bucket.check_content()

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket.restore(1, dry_run=False)

    logger_mock.error.assert_called_with("Restore failed because the original location unknown.")
    assert exit_info.value.code == errno.EPERM


def test_restore_with_path_exists_error(fake_bucket, fs, mocker):
    path = "test.txt"
    fs.create_file(path)

    fake_bucket.rm(path, force=False, dry_run=False)
    fs.create_file(path)

    logger_mock = mocker.patch("myrm.bucket.logger")

    with pytest.raises(SystemExit) as exit_info:
        fake_bucket.restore(1, dry_run=False)

    logger_mock.error.assert_called_with("Restore failed because the destination path exists.")
    assert exit_info.value.code == errno.EPERM
