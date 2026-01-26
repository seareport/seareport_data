from __future__ import annotations

import logging
import pathlib
import typing as ty

import xarray as xr

from . import _core as core
from ._enforce_literals import enforce_literals

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/72832981/592289
# Types
ETopoDataset = ty.Literal["bedrock", "surface", "geoid"]
ETopoVersion = ty.Literal["2022"]
ETopoResolution = ty.Literal["30sec", "60sec"]
# Constants
ETOPO: ty.Literal["ETOPO"] = "ETOPO"
ETOPO_LATEST_VERSION: ETopoVersion = ty.get_args(ETopoVersion)[-1]


def get_etopo_filename(dataset: ETopoDataset) -> str:
    filename = f"ETOPO1_{dataset}_g_gdal.nc"
    return filename


@ty.overload
def etopo(
    dataset: ETopoDataset,
    resolution: ETopoResolution = "30sec",
    version: ETopoVersion = ETOPO_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: ty.Literal[False] = False,
) -> list[str]: ...
@ty.overload
def etopo(
    dataset: ETopoDataset,
    resolution: ETopoResolution = "30sec",
    version: ETopoVersion = ETOPO_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: ty.Literal[True],
) -> list[pathlib.Path]: ...
def etopo(
    dataset: ETopoDataset,
    resolution: ETopoResolution = "30sec",
    version: ETopoVersion = ETOPO_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: bool = False,
) -> list[str] | list[pathlib.Path]:
    enforce_literals(etopo)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[ETOPO][str(version)][resolution][dataset]
    cache_dir = core.get_cache_path() / ETOPO / version
    filename = str(record["filename"])
    path = cache_dir / filename
    if download and not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        url = str(record["url"])
        core.download(url, path)
    if check_hash:
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
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    **kwargs: ty.Any,
) -> xr.Dataset:
    path = etopo(
        dataset=dataset,
        resolution=resolution,
        version=version,
        download=download,
        check_hash=check_hash,
        registry_url=registry_url,
    )[0]
    if "engine" not in kwargs:
        kwargs["engine"] = "h5netcdf"
    ds = xr.open_dataset(path, **kwargs)
    return ds
