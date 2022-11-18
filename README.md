# MYRM

*MYRM* is the command-line interface tool to manage files and directories on the local or remote machine. It helps to move files or directories to your own created bucket, and record the original path with the deleted date.
You can delete a file or a group of files, use a regular expression to delete a specific group of files or delete a file permanently. The bucket has settable politics, you can set the maximum size of the bucket and self-cleanup time. Also, you can restore files and directories from the bucket.

It provides these main commands:
```bash
    myrm rm                move files and directories to the bucket folder or delete permanently
    myrm show              list files in the bucket
    myrm restore           restore deleted objects
    myrm bucket            manage the bucket
```
Also, it has additional options which can be used with main commands.

## Table of contents

1. [Requirements](#requirements)
2. [Installations](#installation)
3. [Using as the CLI](#using-as-the-cli)
4. [Settings](#settings)
5. [Creating your own settings](#creating-your-own-settings)
6. [Using as a Python library](#using-as-a-python-library)
7. [License](#license-mit)

## Requirements

- python (3.6+)
- pip

##### [Back to Contents](#table-of-contents)


## Installation

You can install *MYRM* using the main package manager right from GitHub using the link:

```bash
pip3 install git+https://github.com/masteroftheworld/myrm.git
```

Also, you can clone the repository and install it manually:

```bash
# Step -- 1.
git clone --depth=1 --branch=master https://github.com/masteroftheworld/myrm.git

# Step -- 2.
cd ./myrm/

# Step -- 3.
python3 setup.py install
```

##### [Back to Contents](#table-of-contents)


## Using as the CLI

Before the first usage, you are to generate a new settings file:
```bash
myrm --generate-config
```
This command creates a settings file at the default path "~/.config/myrm/settings.json" on the working machine.


---

#### `myrm rm`

The command helps you to move files or directories to the bucket folder:
```bash
# Step -- 1.
touch test.txt

# Step -- 2.
myrm rm test.txt

# Step -- 3.
mkdir -p ./a/b/c

# Step -- 4.
myrm rm ./a
```


#### `myrm rm` with `--regex` or `-r` flag

The command helps you to move specific files or directories to the bucket using a regular expression pattern:
```bash
# Step -- 1.
mkdir ./a
cd a

# Step -- 2.
touch test{1..3}.txt
touch test{1..3}.cfg
touch test{1..3}.bin

# Step -- 3.
ls
test1.bin  test1.cfg  test1.txt  test2.bin  test2.cfg  test2.txt  test3.bin  test3.cfg  test3.txt

# Step -- 4.
myrm rm ./ --regex '*1.*'

# Step -- 5.
ls
test2.bin  test2.cfg  test2.txt  test3.bin  test3.cfg  test3.txt
```
**Note:** you need to use quotes in order to protect the pattern from shell expansion.

**Caution:** you are to input a path for `myrm rm` command before you input `--regex` with the regular expression.


#### `myrm rm --force`

Using this command with the "--force" flag helps you to permanently delete files or directories from the working machine:
```bash
# Step -- 1.
touch test.txt

# Step -- 2.
myrm rm --force test.txt

# Step -- 3.
mkdir -p ./a/b/c

# Step -- 4.
myrm rm ./a --force
```

#### `myrm rm --confirm (-c)`

Using this command with the "--confirm" or "-c" flag asks for user confirmation before executing the user's command:
```bash
# Step -- 1.
touch test.txt

# Step -- 2.
myrm rm --confirm test.txt
Do you want to delete it? (yes/no)

# Step -- 3.
yes

```

---
#### `myrm show`

The command shows the table with deleted files and directories:
```bash
# Step -- 1.
touch test1.txt test2.txt
mkdir ./a

# Step -- 2.
myrm rm test1.txt test2.txt ./a

# Step -- 3.
myrm show
+---------+-------+-------------+-------------------------+---------------------+
| Status  | Index | Name        | Original location       | Trashed on          |
+---------+-------+-------------+-------------------------+---------------------+
| Correct | 1     | test1.txt   | /user_name/test1.txt    | 09:58:26 10-04-2022 |
| Correct | 2     | test2.txt   | /user_name/test2.txt    | 09:58:26 10-04-2022 |
| Correct | 3     | a           | /user_name/a            | 09:58:26 10-04-2022 |
+---------+-------+-------------+-------------------------+---------------------+
```
Table's columns name description:
- Status - checking if the method of moving objects to the bucket directory was correct;
- Index - the ordered number of the object in the bucket, it is necessary when you will decide to restore any object from the bucket;
- Name - the name of the object which has moved to the bucket;
- Original location - the path from where the object was moved to the bucket;
- Trashed on - the time when the object was moved to the bucket.

In cases when the object was moved to the bucket directory not using the `myrm` tool the "Status" and the "Original location" would be set as "Unknown" and the "Trashed time" would be set as a time when the object was been modified last time (excluding cases if the object is a symbol link, in these cases "Trashed time" would be set as a time when the object was detected in the bucket directory).


#### `myrm show --limit`

Command with such a flag sets the limit of the table lines on one page:

```
myrm show --limit 2
+---------+-------+-------------+-------------------------+---------------------+
| Status  | Index | Name        | Original location       | Trashed on          |
+---------+-------+-------------+-------------------------+---------------------+
| Correct | 1     | test1.txt   | .../trash_bin/test1.txt | 09:58:26 10-04-2022 |
| Correct | 2     | test2.txt   | .../trash_bin/test2.txt | 09:58:26 10-04-2022 |
+---------+-------+-------------+-------------------------+---------------------+
```
The default limit value is specified as 20.

#### `myrm show --page`

Command with such a flag shows the specified page of the table:
```
myrm show --limit2 --page1
+---------+-------+-------------+-------------------------+---------------------+
| Status  | Index | Name        | Original location       | Trashed on          |
+---------+-------+-------------+-------------------------+---------------------+
| Correct | 1     | test1.txt   | .../trash_bin/test1.txt | 09:58:26 10-04-2022 |
| Correct | 2     | test2.txt   | .../trash_bin/test2.txt | 09:58:26 10-04-2022 |
+---------+-------+-------------+-------------------------+---------------------+

myrm show --limit2 --page2
+---------+-------+-------------+-------------------------+---------------------+
| Status  | Index | Name        | Original location       | Trashed on          |
+---------+-------+-------------+-------------------------+---------------------+
| Correct | 3     | a           | .../trash_bin/a         | 09:58:26 10-04-2022 |
+---------+-------+-------------+-------------------------+---------------------+

```
By default without the `--page` flag it always shows the first page.

___
#### `myrm restore`
This command restores the deleted object from the bucket directory to the original path. To restore the object you are to add its index at the end of the command:

```bash
# Step -- 1.
mkdir ./a
cd ./a
touch test.txt

# Step -- 2.
myrm rm test.txt

# Step -- 3.
myrm show
+---------+-------+-------------+-------------------------+---------------------+
| Status  | Index | Name        | Original location       | Trashed on          |
+---------+-------+-------------+-------------------------+---------------------+
| Correct | 1     | test.txt    | /user_name/a/test.txt   | 09:58:26 10-04-2022 |
+---------+-------+-------------+-------------------------+---------------------+

# Step -- 4.
myrm restore 1

# Step -- 5.
ls
test.txt
```

___
#### `myrm bucket --create`
This command with such a flag creates the bucket folder if it doesn't exist.


___
#### `myrm bucket --cleanup`
This command permanently erases all the bucket's content and the bucket's history:

```bash
# Step -- 1.
touch test1.txt test2.txt
mkdir ./a

# Step -- 2.
myrm rm test1.txt test2.txt ./a

# Step -- 3.
myrm show
+---------+-------+-------------+-------------------------+---------------------+
| Status  | Index | Name        | Original location       | Trashed on          |
+---------+-------+-------------+-------------------------+---------------------+
| Correct | 1     | test1.txt   | /user_name/test1.txt    | 09:58:26 10-04-2022 |
| Correct | 2     | test2.txt   | /user_name/test2.txt    | 09:58:26 10-04-2022 |
| Correct | 3     | a           | /user_name/a            | 09:58:26 10-04-2022 |
+---------+-------+-------------+-------------------------+---------------------+

Step -- 4.
myrm bucket --cleanup

Step -- 5.
myrm show
2022-11-14--11-34-48 - WARNING :: myrm :: Show content of the bucket failed because the main bucket is empty.
```

___
#### [`--dry-run] mode`
All the `myrm` commands support `dry-run` mode. This mode allows you to see what happened if you use a command, but without any real changes in your file system. You can use it by simply adding the "`--dry-run`" flag at the end of the command.
For example:
```bash
# Step -- 1.
touch test.txt

# Step -- 2.
myrm rm test.txt --dry-run

# Step -- 3.
ls
test.txt
myrm show
2022-11-14--11-34-48 - WARNING :: myrm :: Show content of the bucket failed because the main bucket is empty.
```

---
#### [`--debug` | `--silent` | `--verbose`]


Using these flags with the user command will set the level of the logging while executing the user's command:
 - `--debug`   - print a lot of debugging statements while executing the user's commands;
 - `--silent`  - do not print any statements while executing the user's commands;
 - `--verbose` - print verbosely what happens while executing the user's commands.

##### [Back to Contents](#table-of-contents)

---
#### Settings

The default settings file path is "~/.config/myrm/settings.json".
This file includes the next bucket configuration:
- Bucket path - the path of the bucket folder, by default it is "~/.local/share/myrm/trash_bin";
- Bucket history path - the path of the bucket's history, by default it is "~/.local/share/myrm/history.pkl";
- Bucket size - the size of your bucket directory in megabytes, by default it equals 1024 megabytes;
- Bucket storetime - the time how long items in the bucket will be saved until permanently deleted.
##### [Back to Contents](#table-of-contents)

---
#### Creating your own settings
If you want to create your own bucket folder with custom options, you are to create a new JSON file with the settings and change the default file with it.
Also, you can set the necessary options through the console using these flags for commands, but it would be valid just once while the current command runtime:
 - `--bucket-path`
```bash
myrm bucket --bucket-path './my_new_bucket/'
ls
my_new_bucket
```
 - `--bucket-history-path`
```bash
myrm bucket --bucket-history-path './'
ls
history.pkl
```
 - `--bucket-size`
```bash
# Step -- 1.
# Create a file with a size of 4 megabytes.
dd if=/dev/urandom of=output.bin count=4096 bs=1024

# Step -- 2.
# Trying to delete the created file while setting the bucket size to equal 1 megabyte.
myrm rm output.bin --bucket-size 1
2022-04-14--11-16-02 - ERROR :: myrm :: The maximum trash bin size has been exceeded.
```

 - `--bucket-storetime`
```bash
# Step -- 1.
touch test.txt

# Step -- 2.
myrm rm test.txt

# Step -- 3.
myrm show
+---------+-------+-------------+-------------------------+---------------------+
| Status  | Index | Name        | Original location       | Trashed on          |
+---------+-------+-------------+-------------------------+---------------------+
| Correct | 1     | test.txt    | /user_name/a/test.txt   | 09:58:26 10-04-2022 |
+---------+-------+-------------+-------------------------+---------------------+

# Step -- 4.
myrm show --bucket-storetime 0
2022-11-14--11-34-48 - WARNING :: myrm :: Show content of the bucket failed because the main bucket is empty.
```
Also, you could combine all these flags and use them with the different main commands.
##### [Back to Contents](#table-of-contents)

---
## Using as a Python library

Main modules:

 1) bucket.py
 2) rmlib.py
 3) logger.py
 4) settings.py

### bucket.py
The module is used to create and manage the trash bin directory. You could move files and folders to the trash bin or delete them permanently and use different politics to manage your trash bin.

#### bucket.Bucket
The class with built-in methods is used to create and manage trash bin and to save and manage its history.

* `bucket.Bucket.create(dry_run: bool = False) -> None`

This built-in method of the class helps you to create the bucket directory on the working machine.

```python
from myrm.bucket import Bucket

bucket = Bucket()
bucket.create()  # create trash bin directory on the working machine
```

* `bucket.Bucket.rm(path: str, force: bool = False, dry_run: bool = False) -> None`

This built-in method of the class helps you to move any files or directories to the bucket directory on the working machine.

```python
from myrm.bucket import Bucket

bucket = Bucket()
bucket.rm("test.txt")  # move file 'test.txt' to the trash bin directory on the working machine
```

* `bucket.Bucket.cleanup(dry_run: bool = False) -> None`

This built-in method of the class helps you to completely erase all content of the bucket directory on the working machine.

```python
from myrm.bucket import Bucket

bucket = Bucket()
bucket.cleanup()  # completely erase all content of the trash bin and its history
```

* `bucket.Bucket.get_size() -> int`

This built-in method of the class shows you the size of the bucket directory including the size of all content.

```python
from myrm.bucket import Bucket

bucket = Bucket()
bucket.size() #  shows the size of the trash bin in bytes
```

* `bucket.Bucket.timeout_cleanup() -> None`

This built-in method checks the time when content was moved to the trash bin compares it with trash bin store time settings and deletes all the objects which expired the store time.

```python
from myrm.bucket import Bucket

bucket = Bucket()
bucket.timeout_cleanup()  # delete all objects inside the trash bin which have expired store time
```

* `bucket.Bucket.check_content() -> None`

This built-in method checks the content of the trash bin, compares it with trash bin history, and solves all conflicts between it.

```python
from myrm.bucket import Bucket

bucket = Bucket()
bucket.check_content()  # add missing objects and delete all wrong entries in the history
```

* `bucket.Bucket.restore(index: int, dry_run: bool = False) -> None`

This built-in method restores files and directories from the trash bin to its original path on the working machine.

```python
from myrm.bucket import Bucket

bucket = Bucket()
bucket.restore(1)  # restore the object from the trash bin which index equals 1
```

---
#### bucket.BucketHistory
The class with built-in methods is used to manage history of files and directories moved to the trash bin.

* `bucket.cleanup(dry_run: bool = False) -> None`

This built-in method completely erases all entries in the history file.

```python
from myrm.bucket import BucketHistory

bucket_history = BucketHistory()
bucket_history.cleanup()  # delete all data from the history file
```

* `bucket.get_table(page: int = 1, count: int = 10) -> PrettyTable`

This built-in method returns all data from the history file in the structured form of a good-readable table.

```python
from myrm.bucket import BucketHistory
from prettytable import PrettyTable

bucket_history = BucketHistory()
print(bucket_history.gettable())  # show a table of entries from the history file
```

---
### rmlib.py

Using this module you could create, move or delete directories and move or delete files. It contains the folowing functions:
* rmlib.mkdir
* rmlib.rm
* rmlib.rmdir
* rmlib.mv
* rmlib.mvdir

#### rmlib.mkdir
This function creates a new directory on the current machine. It has the following signature:

> rmlib.mkdir(path: str, dry_run: bool = False) -> None

```python
from myrm.rmlib import mkdir

mkdir("test")  # create the "test" directory on the working machine
```

#### rmlib.rm
This function permanently deletes a file from the working machine. It has the next signature:

> rmlib.rm(path: str, dry_run: bool = False) -> None:
```python
from myrm.rmlib import rm

rm("test.txt")  # delete 'test.txt' from the working machine
```

#### rmlib.rmdir
This function recursively and permanently deletes a directory and all included content from the working machine. It has the next signature:

> rmlib.rmdir(path: str, dry_run: bool = False) -> None:
```python
from myrm.rmlib import rmdir

rmdir("test")  # delete 'test' and all included content from the working machine
```

#### rmlib.mv
This function moves a file from one path to another. It has the next signature:

> rmlib.mv(src: str, dst: str, dry_run: bool = False) -> None:
```python
from myrm.rmlib import mv

mv("~/test.txt", "~/a/test.txt")  # move '~/test.txt' to the '~/a/test.txt' on the working machine
```

#### rmlib.mvdir
This function recursively moves a directory and all included content from one path to another. It has the next signature:

> rmlib.mv(src: str, dst: str, dry_run: bool = False) -> None:
```python
from myrm.rmlib import mv

mv("~/test", "~/a/test")  # move directory 'user_name/test' and all included content to 'user_name/a/test'
```
---
### logger.py
This module is used to log and save information about program runtime, warnings, and errors depending on the user's settings.
To use this module you are to include it in your `__init__` file:
```python
from myrm.logger import setup

setup()  # install the logger
```

After that, you are to create the logger and named it "myrm" in every module in which you want to use it:
```python
import logging

logger = logging.getLogger("myrm")  # create the logger instance with settings from myrm.logger
```
---
### settings.py
This module is used to manage the trash bin settings. It includes the class `AppSettings` and two main functions `generate` and `load`.

#### settings.AppSettings
This class is used to instantiate settings. It checks the given settings type and guarantees that settings will be transferred to the trash bin in the required type. There are three types of the settings:
 - PathField            - converts the path to expanduser path;
 - PositiveIntegerField - convert the value to an integer and checks if it is positive;
 - BooleanField         - checks if the value is boolean.
```python
from myrm.settings import AppSettings

app_settings = AppSettings()  # create a new instance of the AppSettings with default options
```

#### settings.generate
This function create the settings file in json format for the trash bin.
> settings.generate(path: str = DEFAULT_SETTINGS_PATH) -> None
```python
from myrm.settings import generate

generate()  # generate the settings file on the default path
```

#### settings.load
This function loads the settings from the determined settings file.
> settings.load(path: str = DEFAULT_SETTINGS_PATH) -> AppSettings
```python
from myrm.settings import load

load("filename.json")  # load the settings from the given file
```
##### [Back to Contents](#table-of-contents)
---
## License MIT
The project License can be found [here](LICENSE.md).
