import logging
from collections.abc import Callable
from typing import Any

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
