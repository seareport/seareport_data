import importlib.metadata

from ._gebco import gebco
from ._gshhg import gshhg

__version__ = importlib.metadata.version(__name__)


__all__: list[str] = [
    "gebco",
    "gshhg",
    "__version__",
]
