import errno
import io
import json
import logging
import os

import pytest

from myrm import settings


def test_load_settings(fs):
    path = "test.json"
    test_settings = {
        "bucket_path": "recycle",
        "bucket_history_path": "history_bucket.pkl",
        "bucket_size": 10,
        "bucket_storetime": 2,
    }

    with io.open(path, mode="wt", encoding="utf-8") as stream_out:
        json.dump(test_settings, stream_out)

    assert os.path.basename(settings.load(path).bucket_path) == test_settings["bucket_path"]


def test_load_settings_with_io_error(fs, mocker):
    logger_mock = mocker.patch("myrm.settings.logger")
    open_mock = mocker.patch("myrm.settings.io.open")
    open_mock.side_effect = IOError(errno.EIO, "")

    with pytest.raises(SystemExit) as exit_info:
        settings.load("")

    logger_mock.error.assert_called_with(
        "It's impossible to load the settings from the current machine."
    )
    assert exit_info.value.code == errno.EIO


def test_load_settings_with_type_error(fs, mocker):
    logger_mock = mocker.patch("myrm.settings.logger")
    open_mock = mocker.patch("myrm.settings.io.open")
    open_mock.side_effect = TypeError(errno.EPERM, "")

    with pytest.raises(SystemExit) as exit_info:
        settings.load("test.txt")

    logger_mock.error.assert_called_with("It's impossible to parse the provided settings scheme.")
    assert exit_info.value.code == errno.EPERM


def test_path_field(mocker, fake_path_field):
    expanduser_mock = mocker.patch("myrm.settings.os.path.expanduser")
    expanduser_mock.side_effect = lambda path: path.replace("~", "/home/user")

    fake_path_field.path = "~/documents/test"
    assert fake_path_field.path == "/home/user/documents/test"


def test_path_field_with_type_error(fake_path_field):
    path = 8

    with pytest.raises(settings.ValidationError) as exit_info:
        fake_path_field.path = path

    assert str(exit_info.value) == "Path must be string but recieved: {0!r}".format(type(path))


def test_path_field_with_empty_path_error(fake_path_field):
    path = ""

    with pytest.raises(settings.ValidationError) as exit_info:
        fake_path_field.path = path

    assert str(exit_info.value) == "Path can not be empty."


def test_positive_integer_field(fake_integer):
    x = 8

    fake_integer.number = 8
    assert fake_integer.number == x


def test_positive_integer_field_with_type_error(fake_integer):
    number = "qwe"

    with pytest.raises(settings.ValidationError) as exit_info:
        fake_integer.number = number

    assert str(exit_info.value) == "Number must be integer but recieved: {0!r}.".format(
        type(number)
    )


def test_positive_integer_field_with_negative_value_error(fake_integer):
    number = -8

    with pytest.raises(settings.ValidationError) as exit_info:
        fake_integer.number = number

    assert str(exit_info.value) == "Number must be positive."


def test_boolean_field(fake_boolean):
    flag = True

    fake_boolean.flag = True
    assert fake_boolean.flag == flag


def test_boolean_field_with_type_error(fake_boolean):
    flag = "test"

    with pytest.raises(settings.ValidationError) as exit_info:
        fake_boolean.flag = flag

    assert str(exit_info.value) == "Flag must be boolean but recieved: {0!r}.".format(type(flag))


def test_app_settings_with_validation_error(caplog):
    test_settings = {
        "bucket_path": "test",
        "bucket_history_path": "test.pkl",
        "bucket_size": "test",
        "bucket_storetime": 2,
    }

    with pytest.raises(SystemExit) as exit_info:
        settings.AppSettings(**test_settings)

    record = caplog.records[0]
    assert record.levelno == logging.ERROR
    assert (
        record.message
        == "The validation process was failed: Number must be integer but recieved: <class 'str'>."
    )
    assert exit_info.value.code == errno.EPERM


def test_generate(fs):
    path = "test/test_settings.json"

    settings.generate(path)
    assert os.path.isfile(path) and os.path.exists(path)


def test_generate_with_error(mocker):
    logger_mock = mocker.patch("myrm.settings.logger")
    open_mock = mocker.patch("myrm.settings.io.open")
    open_mock.side_effect = IOError(errno.EIO, "")

    with pytest.raises(SystemExit) as exit_info:
        settings.generate()

    logger_mock.error.assert_called_with(
        "It's impossible to generate the settings on the current machine."
    )
    assert exit_info.value.code == errno.EIO
