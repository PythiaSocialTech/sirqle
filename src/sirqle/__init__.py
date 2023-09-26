import importlib.metadata

__version__ = importlib.metadata.version(__package__ or __name__)
from src.sirqle.config import Config
from src.sirqle.query import Query
