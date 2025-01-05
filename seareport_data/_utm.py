from __future__ import annotations

import dataclasses
import functools

import geopandas as gpd
import shapely
from shapely import box

# https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system#
# This is essentially a static dataset but it doesn't seem to be readily downloadable.
# The only sourcews I found were from ArcGIS and they needed to be converted
# Recreating is not that hard, so this is what we do here.
# We avoid the need to host it, too.


@dataclasses.dataclass
class Tile:
    zone: int
    row: str
    code: str
    geometry: shapely.Polygon


@functools.cache
def utm_df() -> gpd.GeoDataFrame:
    tiles: list[Tile] = []

    # South Pole
    tiles.extend(
        [
            Tile(0, "A", "esri:102021", box(-180, -90, 0, -80)),
            Tile(0, "B", "esri:102021", box(0, -90, 180, -80)),
        ],
    )

    for zone in range(1, 61):
        # southern hemisphere
        for i, row in enumerate("CDEFGHJKLM"):
            polygon = box((zone - 1) * 6 - 180, -80 + i * 8, zone * 6 - 180, -80 + (i + 1) * 8)
            tiles.append(Tile(zone, row, f"epsg:327{zone:02d}", polygon))
        # northern hemisphere
        for i, row in enumerate("NPQRSTUVW"):
            polygon = box((zone - 1) * 6 - 180, i * 8, zone * 6 - 180, (i + 1) * 8)
            tiles.append(Tile(zone, row, f"epsg:326{zone:02d}", polygon))
        # row X
        if zone in (32, 34, 36):
            continue
        polygon = box((zone - 1) * 6 - 180, 72, zone * 6 - 180, 84)
        tiles.append(Tile(zone, "X", f"epsg:326{zone:02d}", polygon))

    # North Pole
    tiles.extend(
        [
            Tile(0, "X", "esri:102018", box(-180, 84, 0, 90)),
            Tile(0, "Y", "esri:102018", box(0, 84, 180, 90)),
        ],
    )

    utm = gpd.GeoDataFrame(tiles, crs=4326)

    # Apply Norway exceptions
    utm.loc[(utm.zone == 31) & (utm.row == "V"), "geometry"] = shapely.box(0, 56, 3, 64)  # noqa: PLR2004
    utm.loc[(utm.zone == 32) & (utm.row == "V"), "geometry"] = shapely.box(3, 56, 12, 64)  # noqa: PLR2004
    utm.loc[(utm.zone == 31) & (utm.row == "X"), "geometry"] = shapely.box(0, 72, 9, 84)  # noqa: PLR2004
    utm.loc[(utm.zone == 33) & (utm.row == "X"), "geometry"] = shapely.box(9, 72, 21, 84)  # noqa: PLR2004
    utm.loc[(utm.zone == 35) & (utm.row == "X"), "geometry"] = shapely.box(21, 72, 33, 84)  # noqa: PLR2004
    utm.loc[(utm.zone == 37) & (utm.row == "X"), "geometry"] = shapely.box(33, 72, 42, 84)  # noqa: PLR2004

    return utm
