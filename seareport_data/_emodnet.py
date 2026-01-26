from __future__ import annotations

import logging
import pathlib
import typing as ty

from . import _core as core
from ._enforce_literals import enforce_literals

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/72832981/592289
# Types
EMODnetVersion = ty.Literal["2022"]
# Constants
EMODNET: ty.Literal["EMODnet"] = "EMODnet"
EMODNET_LATEST_VERSION: EMODnetVersion = ty.get_args(EMODnetVersion)[-1]


@ty.overload
def emodnet(
    version: EMODnetVersion = EMODNET_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: ty.Literal[False] = False,
) -> list[str]: ...
@ty.overload
def emodnet(
    version: EMODnetVersion = EMODNET_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: ty.Literal[True],
) -> list[pathlib.Path]: ...
def emodnet(
    version: EMODnetVersion = EMODNET_LATEST_VERSION,
    *,
    download: bool = True,
    check_hash: bool = True,
    registry_url: str | None = None,
    as_paths: bool = False,
) -> list[str] | list[pathlib.Path]:
    enforce_literals(emodnet)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[EMODNET][str(version)]
    base_url = ty.cast(str, record["base_url"])
    cache_dir = core.get_cache_path() / EMODNET / version
    paths: list[pathlib.Path] = []
    for filename, expected_hash in record["hashes"].items():
        assert isinstance(filename, str)
        assert isinstance(expected_hash, str)
        archive = cache_dir / f"{filename}.zip"
        path = cache_dir / filename
        if download and not path.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            url = f"{base_url}{filename}.zip"
            core.download(url, archive)
            core.extract_zip(archive=archive, filename=filename, target_dir=cache_dir)
            if check_hash:
                core.check_hash(path, expected_hash)
            core.lenient_remove(archive)
        paths.append(path)
    if as_paths:
        return paths
    else:
        return [str(path) for path in paths]


# def emodnet_ds(
#     version: EMODnetVersion = EMODNET_LATEST_VERSION,
#     *,
#     registry_url: str | None = None,
#     **kwargs: T.Any,
# ) -> xr.Dataset:
#     paths = emodnet(
#         version=version,
#         registry_url=registry_url,
#     )
#     if "engine" not in kwargs:
#         kwargs["engine"] = "h5netcdf"
#     ds = xr.open_dataset(paths, **kwargs)
#     return ds
