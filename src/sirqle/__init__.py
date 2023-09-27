import importlib.metadata

__version__ = importlib.metadata.version(__package__ or __name__)
from .config import Config
from .query import Query
