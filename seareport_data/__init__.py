import importlib.metadata

from ._gebco import gebco
from ._gshhg import gshhg
from ._rtopo import rtopo
from ._srtm15p import srtm15p

__version__ = importlib.metadata.version(__name__)


__all__: list[str] = [
    "gebco",
    "gshhg",
    "rtopo",
    "srtm15p",
    "__version__",
]
