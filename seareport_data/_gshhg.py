import typing as T

from . import _core as core

CRUDE: T.Literal["crude"] = "crude"
LOW: T.Literal["low"] = "low"
INTERMEDIATE: T.Literal["intermediate"] = "intermediate"
HIGH: T.Literal["high"] = "high"
FULL: T.Literal["full"] = "full"

GSHHG: T.Literal["GSHHG"] = "GSHHG"
GSHHG_CRUDE_L5: T.Literal["crude_l5"] = "crude_l5"
GSHHG_CRUDE_L6: T.Literal["crude_l6"] = "crude_l6"

GSHHG_V237_1: T.Literal["2.3.7.1"] = "2.3.7.1"
GSHHG_V237_2: T.Literal["2.3.7.2"] = "2.3.7.2"
GSHHG_V237_3: T.Literal["2.3.7.3"] = "2.3.7.3"
GSHHG_LATEST = GSHHG_V237_1

# https://stackoverflow.com/a/72832981/592289
# Types
Records = T.Literal["GSHHG"]
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
# CONSTANTS
RECORDS: set[Records] = set(T.get_args(Records))
GSHHG_RESOLUTIONS: set[GSHHGResolution] = set(T.get_args(GSHHGResolution))
GSHHG_SHORELINES: set[GSHHGShoreline] = set(T.get_args(GSHHGShoreline))

SHORT_TO_LONG_GSHHG_RESOLUTIONS = {
    "c": CRUDE,
    "l": LOW,
    "i": INTERMEDIATE,
    "h": HIGH,
    "f": FULL,
}

_GSHHG_ALLOWED = set(core._load_registry()[GSHHG].keys())


def _assert_gshhg_resolution_is_valid(resolution: str) -> T.TypeGuard[GSHHGResolution]:
    msg = f"resolution must be one of: {GSHHG_RESOLUTIONS}, not {resolution}"
    assert resolution[0].lower() in GSHHG_RESOLUTIONS, msg
    return True


def _assert_gshhg_shoreline_is_valid(shoreline: str | int) -> T.TypeGuard[GSHHGShoreline]:
    msg = f"shoreline must be one of: {GSHHG_SHORELINES}, not {shoreline}"
    assert shoreline in GSHHG_SHORELINES, msg
    return True


def _get_gshhg_filename(
    resolution: GSHHGResolution,
    shoreline: GSHHGShoreline,
) -> str:
    short_resolution = resolution[0].lower()
    long_resolution = SHORT_TO_LONG_GSHHG_RESOLUTIONS[short_resolution]
    return f"gshhg_{long_resolution}_l{shoreline}.gpkg"


def fetch_gshhg(
    resolution: GSHHGResolution,
    shoreline: GSHHGShoreline,
    version: str = GSHHG_LATEST,
) -> str:
    # sanity check
    _assert_gshhg_resolution_is_valid(resolution)
    _assert_gshhg_shoreline_is_valid(shoreline)

    filename = _get_gshhg_filename(resolution=resolution, shoreline=shoreline)
    core._is_version_valid(record=GSHHG, filename=filename, version=version, allowed=_GSHHG_ALLOWED)
    # filename = _get_gshhg_filename(identifier=identifier)
    # hash = core._load_registry()[GSHHG][identifier][version]["hash"]
    repo = core._get_repository(
        record=GSHHG,
        version=version,
        filename=filename,
    )
    path: str = repo.fetch(filename)
    return path
