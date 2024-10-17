import importlib.metadata

from ._etopo import etopo
from ._etopo import etopo_ds
from ._gebco import gebco
from ._gebco import gebco_ds
from ._gshhg import gshhg
from ._gshhg import gshhg_df
from ._rtopo import rtopo
from ._rtopo import rtopo_ds
from ._srtm15p import srtm15p
from ._srtm15p import srtm15p_ds

__version__ = importlib.metadata.version(__name__)


__all__: list[str] = [
    "etopo",
    "etopo_ds",
    "gebco",
    "gebco_ds",
    "gshhg",
    "gshhg_df",
    "rtopo",
    "rtopo_ds",
    "srtm15p",
    "srtm15p_ds",
    "__version__",
]
