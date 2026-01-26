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
COPERNICUSDataset = T.Literal["bathy"]
COPERNICUSBathyVersion = T.Literal["202511"]
COPERNICUSVersion = COPERNICUSBathyVersion
# Constants
COPERNICUS: T.Literal["COPERNICUS"] = "COPERNICUS"
BATHY: T.Literal["BATHY"] = "BATHY"


def resolve_version(dataset: COPERNICUSDataset) -> COPERNICUSVersion:
    if dataset == "bathy":
        latest: COPERNICUSVersion = T.get_args(COPERNICUSBathyVersion)[-1]
    else:
        raise ValueError(f"Unknown dataset: {dataset}")
    return latest


class COPERNICUSRecord(T.TypedDict):
    dataset_id: str
    filename: str
    hash: str


def copernicus(
    dataset: COPERNICUSDataset = "bathy",
    version: COPERNICUSBathyVersion | None = None,
    *,
    download: bool = True,
    check_hash: bool = True,
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
    import copernicusmarine

    enforce_literals(copernicus)
    version = resolve_version(dataset)
    cache_dir = core.get_cache_path() / COPERNICUS / dataset / version
    registry = core.load_registry(registry_url=registry_url)
    record: COPERNICUSRecord = registry[COPERNICUS][dataset][version]
    file_path = cache_dir / record["filename"]
    if download and not file_path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        _ = copernicusmarine.get(
            dataset_id=record["dataset_id"],
            dataset_version=version,
            no_directories=True,
            output_directory=cache_dir,
        )
    if check_hash:
        core.check_hash(file_path, record["hash"])
    if as_paths:
        return [pathlib.Path(file_path)]
    else:
        return [str(file_path)]


def copernicus_ds(
    dataset: COPERNICUSDataset = "bathy",
    version: COPERNICUSBathyVersion | None = None,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    **kwargs: T.Any,
) -> xr.Dataset:
    path = copernicus(
        dataset=dataset,
        version=version,
        download=download,
        check_hash=check_hash,
        registry_url=registry_url,
    )[0]
    if "engine" not in kwargs:
        kwargs["engine"] = "h5netcdf"

    ds = xr.open_dataset(path, **kwargs)
    return ds
