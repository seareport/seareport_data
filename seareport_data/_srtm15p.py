from __future__ import annotations

import logging
import typing as T

from . import _core as core

logger = logging.getLogger(__name__)

# Constants

# https://stackoverflow.com/a/72832981/592289
# Types
SRTM15PVersion = T.Literal["2.6"]
# Constants
SRTM15P: T.Literal["SRTM15+"] = "SRTM15+"
SRTM15P_LATEST_VERSION: SRTM15PVersion = T.get_args(SRTM15PVersion)[-1]


class SRTM15PRecord(T.TypedDict):
    url: str
    filename: str
    hash: str


def srtm15p(
    version: SRTM15PVersion = SRTM15P_LATEST_VERSION,
    *,
    registry_url: str | None = None,
) -> str:
    """
    Return the path to a SRTM15+ dataset, downloading the dataset if necessary.

    Parameters:
        version: The SRTM15+ version to use. Defaults to the latest version available.
        registry_url: The URL to a registry that provides the dataset metadata.
            If None, the default registry is used.

    Returns:
        str: The path of the requested SRTM15+ dataset in the local cache.

    """
    core.enforce_literals(srtm15p)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[SRTM15P][version]
    cache = core.get_cache_path() / SRTM15P / version
    cache.mkdir(parents=True, exist_ok=True)
    file_path = cache / record["filename"]
    if not file_path.exists():
        core.download(record["url"], file_path)
    core.check_hash(file_path, record["hash"])
    return str(file_path)