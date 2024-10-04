from __future__ import annotations

import logging
import typing as T

from . import _core as core

logger = logging.getLogger(__name__)

# https://stackoverflow.com/a/72832981/592289
# Types
GSHHGVersion = T.Literal["2.3.7.1"]
GSHHGResolution = T.Literal[
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
GSHHGShoreline = T.Literal[5, 6, "5", "6"]
# Constants
GSHHG: T.Literal["GSHHG"] = "GSHHG"
CRUDE: T.Literal["crude"] = "crude"
LOW: T.Literal["low"] = "low"
INTERMEDIATE: T.Literal["intermediate"] = "intermediate"
HIGH: T.Literal["high"] = "high"
FULL: T.Literal["full"] = "full"
GSHHG_LATEST_VERSION: GSHHGVersion = sorted(T.get_args(GSHHGVersion))[-1]


class GSHHGRecord(T.TypedDict):
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


def gshhg(
    resolution: GSHHGResolution,
    shoreline: GSHHGShoreline,
    version: GSHHGVersion = GSHHG_LATEST_VERSION,
    *,
    registry_url: str | None = None,
) -> str:
    core.enforce_literals(gshhg)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[GSHHG][version]
    cache_dir = core.get_cache_path() / GSHHG / version
    filename = get_gshhg_filename(resolution=resolution, shoreline=shoreline)
    path = cache_dir / filename
    if not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        url = record["base_url"] + filename
        core.download(url, path)
    core.check_hash(path, record["hashes"][filename])
    return str(path)
