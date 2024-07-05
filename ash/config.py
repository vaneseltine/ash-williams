import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from xdg import BaseDirectory

logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s - %(levelname)s - %(message)s",
    format="%(asctime)s %(message)s",
    datefmt="%H:%M",
    handlers=[logging.FileHandler("ash.log"), logging.StreamHandler()],
)


def log_this(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(__name__)
        logger.info(f"{func.__name__} | in  | {args}, {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} | out | {result}")
        return result

    return wrapper


WINDOWS = sys.platform.startswith("win")
LINUX = sys.platform.startswith("linux")


def get_data_app_dir() -> Path:

    if xdg_auto_create := BaseDirectory.save_data_path("ash"):
        print("xdg", xdg_auto_create)
        return Path(xdg_auto_create)

    root = get_data_root()
    if root is None:
        raise FileNotFoundError("Not sure where to keep your config file.")
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError("Not sure where to keep your config file.")
    data_app_dir = root_path / "ash"
    if not data_app_dir.exists():
        data_app_dir.mkdir()
    return data_app_dir


def get_data_root() -> Path | str | None:
    if WINDOWS:
        return os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
    if LINUX:
        if env_home := os.getenv("XDG_DATA_HOME"):
            return env_home
    for possible_directory in [
        Path.home() / "Library",
        Path.home() / ".config",
    ]:
        if possible_directory.exists():
            return possible_directory
    return None


print(BaseDirectory.xdg_data_dirs)

DATA_DIR = get_data_app_dir()
