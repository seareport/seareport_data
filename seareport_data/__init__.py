import importlib.metadata

from ._gshhg import fetch_gshhg

__version__ = importlib.metadata.version(__name__)


__all__: list[str] = [
    "fetch_gshhg",
    "__version__",
]
