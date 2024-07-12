import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, ParamSpec, TypeVar

import platformdirs
import tomlkit

logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s - %(levelname)s - %(message)s",
    format="%(asctime)s %(message)s",
    datefmt="%H:%M",
    handlers=[logging.FileHandler("ash.log"), logging.StreamHandler()],
)

P = ParamSpec("P")
R = TypeVar("R")
V = TypeVar("V")

CONFIG_FILE = Path(platformdirs.user_config_dir("ash-williams")) / "config.toml"

if not CONFIG_FILE.exists():
    CONFIG_FILE.parent.mkdir(parents=True)
    _ = CONFIG_FILE.write_text("""[database]""")


def read_value(*, table: str, key: str) -> str | None:
    if not CONFIG_FILE.exists():
        return None
    return tomlkit.parse(CONFIG_FILE.read_text())[table].get(key)  # type: ignore


def write_value(*, table: str, key: str, value: V) -> V | None:
    if not CONFIG_FILE.exists():
        return None
    current = tomlkit.parse(CONFIG_FILE.read_text())
    current[table][key] = value  # type: ignore
    _ = CONFIG_FILE.write_text(tomlkit.dumps(current))  # type: ignore
    return value


def log_this(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:  # pylint: disable=no-member
        logger = logging.getLogger(__name__)

        incoming_to_log = log_inputs(args, kwargs)

        logger.info(f"{func.__name__} | in  | {incoming_to_log}")

        result = func(*args, **kwargs)

        logger.info(f"{func.__name__} | out | {trim(result)}")

        return result

    return wrapper


def log_inputs(args: Any, kwargs: Any) -> str:
    return ", ".join(trim(x) for x in [args, kwargs] if x)


def trim(item: Any, maxlen: int = 160) -> str:
    stringed = repr(item)
    if not maxlen or len(stringed) <= maxlen:
        return stringed
    return stringed[: maxlen - 3] + "..."
