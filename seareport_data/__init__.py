import importlib.metadata

from ._antgg import antgg
from ._antgg import antgg_ds
from ._emodnet import emodnet
from ._etopo import etopo
from ._etopo import etopo_ds
from ._gebco import gebco
from ._gebco import gebco_ds
from ._gshhg import gshhg
from ._gshhg import gshhg_df
from ._ibcao import ibcao
from ._ibcao import ibcao_ds
from ._osm import osm
from ._osm import osm_df
from ._rtopo import rtopo
from ._rtopo import rtopo_ds
from ._srtm15p import srtm15p
from ._srtm15p import srtm15p_ds
from ._utm import utm_df

__version__ = importlib.metadata.version(__name__)


__all__: list[str] = [
    "__version__",
    "antgg",
    "antgg_ds",
    "emodnet",
    "etopo",
    "etopo_ds",
    "gebco",
    "gebco_ds",
    "gshhg",
    "gshhg_df",
    "ibcao",
    "ibcao_ds",
    "osm",
    "osm_df",
    "rtopo",
    "rtopo_ds",
    "srtm15p",
    "srtm15p_ds",
    "utm_df",
]
