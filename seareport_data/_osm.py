from __future__ import annotations

import json
import logging
import os
import pathlib
import typing as T

import geopandas as gpd
import pyogrio

from . import _core as core

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/72832981/592289
# Types
OSMDataset = T.Literal["land"]
OSMVersion = T.Literal["2025-01", "2025-05"]
# Constants
OSM: T.Literal["OSM"] = "OSM"
OSM_LATEST_VERSION: OSMVersion = T.get_args(OSMVersion)[-1]


def read_file(
    filename: str | os.PathLike[str],
    layer: str | None = None,
    **kwargs: T.Any,
) -> gpd.GeoDataFrame:
    info = pyogrio.read_info(filename, layer=layer, **kwargs)
    gdf = T.cast(gpd.GeoDataFrame, gpd.read_file(filename, engine="pyogrio", layer=layer, **kwargs))
    if layer_metadata := info["layer_metadata"]:
        if pandas_attrs := layer_metadata.get("PANDAS_ATTRS"):
            gdf.attrs.update(json.loads(pandas_attrs))
    return gdf


def get_osm_filename(dataset: OSMDataset) -> str:
    filename = f"osm_{dataset}_complete_4326.sqlite"
    return filename


def osm(
    dataset: OSMDataset = "land",
    version: OSMVersion = OSM_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    as_paths: bool = False,
) -> list[core.CachedPaths]:
    core.enforce_literals(osm)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[OSM][str(version)][dataset]
    logger.debug("Record: %s", record)
    cache_dir = core.get_cache_path() / OSM / version
    filename = str(record["filename"])
    path = cache_dir / filename
    if not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        archive_path = cache_dir / record["archive"]
        url = str(record["url"])
        core.download(url, archive_path)
        core.extract_zstd(archive_path, path)
        core.lenient_remove(archive_path)
    core.check_hash(path, str(record["hash"]))
    if as_paths:
        return [pathlib.Path(path)]
    else:
        return [str(path)]


def osm_df(
    dataset: OSMDataset = "land",
    version: OSMVersion = OSM_LATEST_VERSION,
    *,
    registry_url: str | None = None,
    **kwargs: T.Any,
) -> gpd.GeoDataFrame:
    path = osm(
        dataset=dataset,
        version=version,
        registry_url=registry_url,
    )[0]
    gdf: gpd.GeoDataFrame = read_file(path, **kwargs)
    return gdf
