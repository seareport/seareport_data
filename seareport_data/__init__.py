import importlib.metadata

from ._copernicus import copernicus
from ._copernicus import copernicus_ds
from ._emodnet import emodnet
from ._etopo import etopo
from ._etopo import etopo_ds
from ._gebco import gebco
from ._gebco import gebco_ds
from ._gshhg import gshhg
from ._gshhg import gshhg_df
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
    "copernicus",
    "copernicus_ds",
    "emodnet",
    "etopo",
    "etopo_ds",
    "gebco",
    "gebco_ds",
    "gshhg",
    "gshhg_df",
    "osm",
    "osm_df",
    "rtopo",
    "rtopo_ds",
    "srtm15p",
    "srtm15p_ds",
    "utm_df",
]
