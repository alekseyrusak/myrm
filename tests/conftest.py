import os

import pytest


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
