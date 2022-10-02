import os

__all__ = (
    "HOME",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
)

HOME: str = os.path.expanduser("~")

# Where user-specific configurations should be written.
XDG_CONFIG_HOME: str = os.path.join(HOME, ".config", "myrm")

# Where user-specific data files should be written.
XDG_DATA_HOME: str = os.path.join(HOME, ".local", "share", "myrm")
