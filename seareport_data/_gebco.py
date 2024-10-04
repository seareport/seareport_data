from __future__ import annotations

import logging
import typing as T

from . import _core as core

logger = logging.getLogger(__name__)

# Constants

# https://stackoverflow.com/a/72832981/592289
# Types
GEBCODatasets = T.Literal["ice", "sub_ice"]
GEBCOVersion = T.Literal[2023, 2024, "2023", "2024"]
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
) -> str:
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
    core.enforce_literals(gebco)
    registry = core.load_registry(registry_url=registry_url)
    version_str = str(version)
    record = registry[GEBCO][version_str][dataset]
    cache = core.get_cache_path() / GEBCO / version_str / dataset
    cache.mkdir(parents=True, exist_ok=True)
    file_path = cache / record["filename"]
    archive_path = cache / record["archive"]
    if not file_path.exists():
        core.download(record["url"], archive_path)
        core.extract(archive_path, record["filename"], cache)
    core.check_hash(file_path, record["hash"])
    core.lenient_remove(archive_path)
    return str(file_path)