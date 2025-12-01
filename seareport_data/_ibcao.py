import logging
import pathlib
import typing as T

import xarray as xr

from . import _core as core
from ._enforce_literals import enforce_literals

logger = logging.getLogger(__name__)

# https://stackoverflow.com/a/72832981/592289
# Types
IBCAODataset = T.Literal["ice", "bedrock"]
IBCAOVersion = T.Literal["2025"]
IBCAOResolution = T.Literal["100m", "200m", "400m"]
# Constants
IBCAO: T.Literal["IBCAO"] = "IBCAO"
IBCAO_LATEST_VERSION: IBCAOVersion = T.get_args(IBCAOVersion)[-1]


class IBCAORecord(T.TypedDict):
    url: str
    filename: str
    hash: str


def ibcao(
    dataset: IBCAODataset,
    resolution: IBCAOResolution,
    version: IBCAOVersion = IBCAO_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    as_paths: bool = False,
) -> list[core.CachedPaths]:
    enforce_literals(ibcao)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[IBCAO][str(version)][resolution][dataset]
    cache_dir = core.get_cache_path() / IBCAO / version / dataset
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


def ibcao_ds(
    dataset: IBCAODataset,
    resolution: IBCAOResolution,
    version: IBCAOVersion = IBCAO_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    **kwargs: T.Any,
) -> xr.Dataset:
    path = ibcao(
        dataset=dataset,
        resolution=resolution,
        version=version,
        registry_url=registry_url,
    )[0]
    if "engine" not in kwargs:
        kwargs["engine"] = "rasterio"
    ds = xr.open_dataset(path, **kwargs)
    return ds
