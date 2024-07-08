import logging
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s - %(levelname)s - %(message)s",
    format="%(asctime)s %(message)s",
    datefmt="%H:%M",
    handlers=[logging.FileHandler("ash.log"), logging.StreamHandler()],
)

P = ParamSpec("P")
R = TypeVar("R")


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
