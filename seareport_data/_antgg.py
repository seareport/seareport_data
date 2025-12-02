import logging
import pathlib
import typing as T

import xarray as xr

from . import _core as core
from ._enforce_literals import enforce_literals

logger = logging.getLogger(__name__)

# https://stackoverflow.com/a/72832981/592289
# Types
ANTGGVersion = T.Literal["2022"]
# Constants
ANTGG: T.Literal["ANTGG"] = "ANTGG"
ANT_LATEST_VERSION: ANTGGVersion = T.get_args(ANTGGVersion)[-1]


class IBCAORecord(T.TypedDict):
    url: str
    filename: str
    hash: str


def antgg(
    version: ANTGGVersion = ANT_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    as_paths: bool = False,
) -> list[core.CachedPaths]:
    enforce_literals(antgg)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[ANTGG][str(version)]
    cache_dir = core.get_cache_path() / ANTGG / version
    path = cache_dir / record["filename"]
    if not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        url = str(record["url"])
        core.download(url, path)
    core.check_hash(path, str(record["hash"]))
    if as_paths:
        return [pathlib.Path(path)]
    else:
        return [str(path)]


def antgg_ds(
    version: ANTGGVersion = ANT_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    **kwargs: T.Any,
) -> xr.Dataset:
    path = antgg(
        version=version,
        registry_url=registry_url,
    )[0]
    if "engine" not in kwargs:
        kwargs["engine"] = "rasterio"
    ds = xr.open_dataset(path, **kwargs)
    return ds
