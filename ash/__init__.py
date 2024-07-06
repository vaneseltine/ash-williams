"""Ash"""

import importlib.metadata

from .ash import Paper, RetractionDatabase, run_cli

__version__ = importlib.metadata.version("ash")
