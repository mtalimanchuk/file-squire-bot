from pathlib import Path


PATH_MAP = {
    # add your paths (full or relative) here
    # "alias": "path/to/file"
    "me": "squire.log",
    "flask": "myflaskapp/logs/errors.log",
}

PATHS = {key.lower(): Path(value) for key, value in PATH_MAP.items()}
