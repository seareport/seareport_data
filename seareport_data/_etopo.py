from __future__ import annotations

import logging
import pathlib
import typing as T

import xarray as xr

from . import _core as core

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/72832981/592289
# Types
ETopoDataset = T.Literal["bedrock", "surface", "geoid"]
ETopoVersion = T.Literal["2022"]
ETopoResolution = T.Literal["30sec", "60sec"]
# Constants
ETOPO: T.Literal["ETOPO"] = "ETOPO"
ETOPO_LATEST_VERSION: ETopoVersion = T.get_args(ETopoVersion)[-1]


def get_etopo_filename(dataset: ETopoDataset) -> str:
    filename = f"ETOPO1_{dataset}_g_gdal.nc"
    return filename


def etopo(
    dataset: ETopoDataset,
    resolution: ETopoResolution = "30sec",
    version: ETopoVersion = ETOPO_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    as_paths: bool = False,
) -> core.CachedPaths:
    core.enforce_literals(etopo)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[ETOPO][str(version)][resolution][dataset]
    cache_dir = core.get_cache_path() / ETOPO / version
    filename = str(record["filename"])
    path = cache_dir / filename
    if not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        url = str(record["url"])
        core.download(url, path)
    core.check_hash(path, str(record["hash"]))
    if as_paths:
        return [pathlib.Path(path)]
    else:
        return [str(path)]


def etopo_ds(
    dataset: ETopoDataset,
    resolution: ETopoResolution = "30sec",
    version: ETopoVersion = ETOPO_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    **kwargs: T.Any,
) -> xr.Dataset:
    path = etopo(
        dataset=dataset,
        resolution=resolution,
        version=version,
        registry_url=registry_url,
    )[0]
    if "engine" not in kwargs:
        kwargs["engine"] = "h5netcdf"
    ds = xr.open_dataset(path, **kwargs)
    return ds
