from __future__ import annotations

import logging
import typing as T

from . import _core as core

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/72832981/592289
# Types
RTopoVersion = T.Literal["2.0.4"]
RTopoDataset = T.Literal["bedrock", "ice_base", "ice_thickness", "surface_elevation"]
# Constants
RTOPO: T.Literal["RTOPO"] = "RTOPO"
RTOPO_LATEST_VERSION: RTopoVersion = sorted(T.get_args(RTopoVersion))[-1]


def get_rtopo_filename(dataset: RTopoDataset, version: RTopoVersion) -> str:
    dataset_name = str(dataset)
    if dataset in ("bedrock", "ice_base"):
        dataset_name += "_topography"
    filename = f"RTopo-{version}_30sec_{dataset_name}.nc"
    return filename


def rtopo(
    dataset: RTopoDataset,
    version: RTopoVersion = RTOPO_LATEST_VERSION,
    *,
    registry_url: str | None = None,
) -> str:
    core.enforce_literals(rtopo)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[RTOPO][version]
    cache_dir = core.get_cache_path() / RTOPO / version
    filename = get_rtopo_filename(dataset=dataset, version=version)
    path = cache_dir / filename
    if not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        url = record["base_url"] + filename
        core.download(url, path)
    core.check_hash(path, record["hashes"][filename])
    return str(path)
