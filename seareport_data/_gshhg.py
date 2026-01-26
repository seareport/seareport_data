from __future__ import annotations

import logging
import pathlib
import typing as ty

import geopandas as gpd

from . import _core as core
from ._enforce_literals import enforce_literals

logger = logging.getLogger(__name__)

# https://stackoverflow.com/a/72832981/592289
# Types
GSHHGVersion = ty.Literal["2.3.7.1"]
GSHHGResolution = ty.Literal[
    "c",
    "l",
    "i",
    "h",
    "f",
    "C",
    "L",
    "I",
    "H",
    "F",
    "crude",
    "low",
    "intermediate",
    "high",
    "full",
]
GSHHGShoreline = ty.Literal["5", "6"]
# Constants
GSHHG: ty.Literal["GSHHG"] = "GSHHG"
CRUDE: ty.Literal["crude"] = "crude"
LOW: ty.Literal["low"] = "low"
INTERMEDIATE: ty.Literal["intermediate"] = "intermediate"
HIGH: ty.Literal["high"] = "high"
FULL: ty.Literal["full"] = "full"
GSHHG_LATEST_VERSION: GSHHGVersion = sorted(ty.get_args(GSHHGVersion))[-1]


class GSHHGRecord(ty.TypedDict):
    doi: str
    base_url: str
    hashes: dict[str, str]


SHORT_TO_LONG_GSHHG_RESOLUTIONS = {
    "c": CRUDE,
    "l": LOW,
    "i": INTERMEDIATE,
    "h": HIGH,
    "f": FULL,
}


def get_gshhg_filename(
    resolution: GSHHGResolution,
    shoreline: GSHHGShoreline,
) -> str:
    short_resolution = resolution[0].lower()
    long_resolution = SHORT_TO_LONG_GSHHG_RESOLUTIONS[short_resolution]
    return f"gshhg_{long_resolution}_l{shoreline}.gpkg"


@ty.overload
def gshhg(
    resolution: GSHHGResolution,
    shoreline: GSHHGShoreline,
    version: GSHHGVersion = GSHHG_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: ty.Literal[False] = False,
) -> list[str]: ...
@ty.overload
def gshhg(
    resolution: GSHHGResolution,
    shoreline: GSHHGShoreline,
    version: GSHHGVersion = GSHHG_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: ty.Literal[True],
) -> list[pathlib.Path]: ...
def gshhg(
    resolution: GSHHGResolution,
    shoreline: GSHHGShoreline,
    version: GSHHGVersion = GSHHG_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: bool = False,
) -> list[str] | list[pathlib.Path]:
    enforce_literals(gshhg)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[GSHHG][version]
    cache_dir = core.get_cache_path() / GSHHG / version
    filename = get_gshhg_filename(resolution=resolution, shoreline=shoreline)
    path = cache_dir / filename
    if download and not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        url = record["base_url"] + filename
        core.download(url, path)
    if check_hash:
        core.check_hash(path, record["hashes"][filename])
    if as_paths:
        return [pathlib.Path(path)]
    else:
        return [str(path)]


def gshhg_df(
    resolution: GSHHGResolution,
    shoreline: GSHHGShoreline,
    version: GSHHGVersion = GSHHG_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    **kwargs: ty.Any,
) -> gpd.GeoDataFrame:
    path = gshhg(
        resolution=resolution,
        shoreline=shoreline,
        version=version,
        download=download,
        check_hash=check_hash,
        registry_url=registry_url,
    )[0]
    gdf: gpd.GeoDataFrame = gpd.read_file(path, **kwargs)
    return gdf
