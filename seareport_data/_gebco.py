from __future__ import annotations

import logging
import pathlib
import typing as T

import xarray as xr

from . import _core as core
from ._enforce_literals import enforce_literals

logger = logging.getLogger(__name__)

# Constants

# https://stackoverflow.com/a/72832981/592289
# Types
GEBCODatasets = T.Literal["ice", "sub_ice"]
GEBCOVersion = T.Literal["2021", "2022", "2023", "2024", "2025"]
# Constants
GEBCO: T.Literal["GEBCO"] = "GEBCO"
GEBCO_LATEST_VERSION: GEBCOVersion = T.get_args(GEBCOVersion)[-1]


class GEBCORecord(T.TypedDict):
    url: str
    archive: str
    filename: str
    hash: str


def gebco(
    dataset: GEBCODatasets,
    version: GEBCOVersion = GEBCO_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    as_paths: bool = False,
) -> list[core.CachedPaths]:
    """
    Return the path to a GEBCO dataset, downloading the dataset if necessary.

    Parameters:
        dataset: The name of the GEBCO dataset. Possible values: `ice`, `sub_ice`.
        version: The GEBCO version to use. Defaults to the latest version available.
        registry_url: The URL to a registry that provides the dataset metadata.
            If None, the default registry is used.

    Returns:
        str: The path of the requested GEBCO dataset in the local cache.

    """
    enforce_literals(gebco)
    registry = core.load_registry(registry_url=registry_url)
    version_str = str(version)
    record = registry[GEBCO][version_str][dataset]
    cache_dir = core.get_cache_path() / GEBCO / version_str / dataset
    file_path = cache_dir / record["filename"]
    if not file_path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        if "archive" in record:
            archive_path = cache_dir / record["archive"]
            core.download(record["url"], archive_path)
            core.extract_zip(archive_path, record["filename"], cache_dir)
            core.lenient_remove(archive_path)
        else:
            core.download(record["url"], file_path)
    core.check_hash(file_path, record["hash"])
    if as_paths:
        return [pathlib.Path(file_path)]
    else:
        return [str(file_path)]


def gebco_ds(
    dataset: GEBCODatasets,
    version: GEBCOVersion = GEBCO_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    **kwargs: T.Any,
) -> xr.Dataset:
    path = gebco(
        dataset=dataset,
        version=version,
        registry_url=registry_url,
    )[0]
    if "engine" not in kwargs:
        kwargs["engine"] = "h5netcdf"
    ds = xr.open_dataset(path, **kwargs)
    return ds
