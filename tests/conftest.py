import os

import pytest

from myrm import bucket, settings


@pytest.fixture
def fake_tree(fs):
    paths = []

    # Step -- 1.
    root = "dir"
    fs.create_dir(root)
    paths.append(root)

    # Step -- 2.
    path = os.path.join(root, "test.txt")
    fs.create_file(path)
    paths.append(path)

    # Step -- 3.
    path = os.path.join(root, "inner_dir")
    fs.create_dir(path)
    paths.append(path)

    # Step -- 4.
    path = os.path.join(path, "inner_test.txt")
    fs.create_file(path)
    paths.append(path)

    return paths


@pytest.fixture
def fake_bucket(fs):
    test_bucket = bucket.Bucket(path="trash", history_path="history.pkl")
    test_bucket.create(dry_run=False)

    return test_bucket


@pytest.fixture
def fake_bucket_history(fs):
    return bucket.BucketHistory(path="history.pkl")


@pytest.fixture
def fake_entry():
    return bucket.Entry(
        status=bucket.Status.CORRECT.value,
        index=1,
        name="test.txt",
        path="test.txt",
        date="12:03:12",
        origin="test.txt",
    )


@pytest.fixture
def fake_path_field():
    class Mock:
        path = settings.PathField()

    return Mock()


@pytest.fixture
def fake_integer():
    class Mock:
        number = settings.PositiveIntegerField()

    return Mock()


@pytest.fixture
def fake_boolean():
    class Mock:
        flag = settings.BooleanField()

    return Mock()
