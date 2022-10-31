import errno
import logging
import os

import pytest

from myrm.rmlib import mkdir, mv, mvdir, rm, rmdir


def test_mkdir(mocker, caplog, fs):  # pylint: disable=unused-argument
    logger_mock = mocker.patch("myrm.rmlib.logger")
    path = "dir"

    with caplog.at_level(logging.INFO, logger="myrm"):
        mkdir(path, dry_run=False)

    logger_mock.info.assert_called_with("Directory '%s' was created.", path)
    assert os.path.exists(path) and os.path.isdir(path)


def test_mkdir_with_dry_run(mocker, caplog, fs):  # pylint: disable=unused-argument
    logger_mock = mocker.patch("myrm.rmlib.logger")
    path = "dir"

    with caplog.at_level(logging.INFO, logger="myrm"):
        mkdir(path, dry_run=True)

    logger_mock.info.assert_called_with("Directory '%s' was created.", path)
    assert not os.path.exists(path)


def test_mkdir_with_error_exists(fake_tree):
    path = fake_tree[0]
    mkdir(path, dry_run=False)

    assert os.path.exists(path) and os.path.isdir(path)


def test_rm(fs, mocker, caplog):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    path = "test.txt"
    fs.create_file(path)

    with caplog.at_level(logging.INFO, logger="myrm"):
        rm(path, dry_run=False)

    logger_mock.info.assert_called_with("Item '%s' was deleted from the current machine.", path)
    assert not os.path.exists(path)


def test_rm_with_dry_run(fs, mocker, caplog):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    path = "test.txt"
    fs.create_file(path)

    with caplog.at_level(logging.INFO, logger="myrm"):
        rm(path, dry_run=True)

    logger_mock.info.assert_called_with("Item '%s' was deleted from the current machine.", path)
    assert os.path.exists(path) and os.path.isfile(path)


def test_rmdir(fake_tree, mocker, caplog):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    path = fake_tree[0]

    with caplog.at_level(logging.INFO, logger="myrm"):
        rmdir(path, dry_run=False)

    logger_mock.info.assert_called_with(
        "Directory '%s' was deleted from the current machine.", path
    )
    assert not os.path.exists(path)


def test_rmdir_with_dry_run(fake_tree, mocker, caplog):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    path = fake_tree[0]

    with caplog.at_level(logging.INFO, logger="myrm"):
        rmdir(path, dry_run=True)

    logger_mock.info.assert_called_with(
        "Directory '%s' was deleted from the current machine.", path
    )
    assert os.path.exists(path) and os.path.isdir(path)


def test_mv(fs, mocker, caplog):
    logger_mock = mocker.patch("myrm.rmlib.logger")

    src = "1.txt"
    fs.create_file(src)
    dst = "2.txt"

    with caplog.at_level(logging.INFO, logger="myrm"):
        mv(src, dst, dry_run=False)

    logger_mock.info.assert_called_with(
        "Item '%s' was moved to '%s' as a destinational path.", src, dst
    )
    assert not os.path.exists(src) and os.path.exists(dst)


def test_mv_with_dry_run(fs, mocker, caplog):
    logger_mock = mocker.patch("myrm.rmlib.logger")

    src = "1.txt"
    fs.create_file(src)
    dst = "2.txt"

    with caplog.at_level(logging.INFO, logger="myrm"):
        mv(src, dst, dry_run=True)

    logger_mock.info.assert_called_with(
        "Item '%s' was moved to '%s' as a destinational path.", src, dst
    )
    assert os.path.exists(src) and not os.path.exists(dst)


def test_mvdir(fake_tree, mocker, caplog):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    src = fake_tree[0]
    dst = "new_dir"

    with caplog.at_level(logging.INFO, logger="myrm"):
        mvdir(src, dst, dry_run=False)

    logger_mock.info.assert_called_with(
        "Directory '%s' was moved to '%s' as a destinational path.", src, dst
    )
    assert not os.path.exists(src) and os.path.exists(dst)

    for path in fake_tree:
        assert os.path.exists(path.replace(src, dst))


def test_mvdir_with_dry_run(fake_tree, mocker, caplog):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    src = fake_tree[0]
    dst = "new_dir"

    with caplog.at_level(logging.INFO, logger="myrm"):
        mvdir(src, dst, dry_run=True)

    logger_mock.info.assert_called_with(
        "Directory '%s' was moved to '%s' as a destinational path.", src, dst
    )
    assert os.path.exists(src) and not os.path.exists(dst)

    for path in fake_tree:
        assert not os.path.exists(path.replace(src, dst))


def test_mkdir_with_error(mocker):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    makedirs_mock = mocker.patch("myrm.rmlib.os.makedirs")
    makedirs_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        mkdir("", dry_run=False)

    logger_mock.error.assert_called_with("Could not create the determined directory.")
    assert exit_info.value.code == errno.EPERM


def test_rm_with_error(mocker):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    remove_mock = mocker.patch("myrm.rmlib.os.remove")
    remove_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        rm("", dry_run=False)

    logger_mock.error.assert_called_with("Item's path can not be deleted from the current machine.")
    assert exit_info.value.code == errno.EPERM


def test_rmdir_walk_with_error(mocker):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    walk_mock = mocker.patch("myrm.rmlib.os.walk")
    walk_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        rmdir("", dry_run=False)

    logger_mock.error.assert_called_with("The determined path not exists on the current machine.")
    assert exit_info.value.code == errno.EPERM


def test_rmdir_inner_with_error(fake_tree, mocker):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    rmdir_mock = mocker.patch("myrm.rmlib.os.rmdir")
    rmdir_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        rmdir(fake_tree[0], dry_run=False)

    logger_mock.error.assert_called_with(
        "The determined path can't be deleted from the current machine."
    )
    assert exit_info.value.code == errno.EPERM


def test_rmdir_with_error(mocker):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    rmdir_mock = mocker.patch("myrm.rmlib.os.rmdir")
    rmdir_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        rmdir("", dry_run=False)

    logger_mock.error.assert_called_with(
        "The determined path can't be deleted from the current machine."
    )
    assert exit_info.value.code == errno.EPERM


def test_mv_with_error(mocker):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    rename_mock = mocker.patch("myrm.rmlib.os.rename")
    rename_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        mv("", "", dry_run=False)

    logger_mock.error.assert_called_with(
        "The determined item can't be moved to the destinational path."
    )
    assert exit_info.value.code == errno.EPERM


def test_mvdir_with_error(mocker):
    logger_mock = mocker.patch("myrm.rmlib.logger")
    walk_mock = mocker.patch("myrm.rmlib.os.walk")
    walk_mock.side_effect = OSError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        mvdir("", "", dry_run=False)

    logger_mock.error.assert_called_with("The determined path not exists on the current machine.")
    assert exit_info.value.code == errno.EPERM
