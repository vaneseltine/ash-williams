"""Ash"""

import importlib.metadata

from .cli import ash_cli
from .main import Paper, RetractionDatabase

__version__ = importlib.metadata.version("ash-williams")
