import importlib.resources
import json
import pathlib
import typing as T
from collections import abc

import pooch


def _load_registry() -> dict[str, dict[str, dict[str, dict[str, str]]]]:
    registry: dict[str, T.Any] = json.load(importlib.resources.open_text("seareport_data", "registry.json"))
    return registry


def _sanitize_url(url: str) -> str:
    if not url.endswith("/"):
        url += "/"
    return url


def _is_version_valid(
    record: str,
    filename: str,
    version: str,
    allowed: abc.Collection[str],
) -> None:
    """
    Check if the version is in the allowed range, raise an error if not.

    Parameters
    ----------
    version : int
        Integer version of the data.
    allowed : set or list
        List or set of allowed values for the version.
    name : str
        Name of the dataset (used in the error message).

    """
    if version not in allowed:
        msg = f"Invalid version={version} for {record}/{filename}. It must be one of {allowed}."
        raise ValueError(msg)


def _get_repository(record: str, filename: str, version: str) -> pooch.Pooch:
    """
    Create the Pooch instance that fetches a dataset of a particular version

    Cache location defaults to ``pooch.os_cache("seareport_data")`` and can be
    overwritten with the ``SEAREPORT_DATA_DIR`` environment variable.

    Parameters
    ----------
    fname : str
        Name of the data file we want to fetch.
    version : int
        Version number of the dataset that we want to fetch.

    Returns
    -------
    repository : :class:`pooch.Pooch`

    """
    registry = _load_registry()
    entry: dict[str, T.Any] = registry[record][version]
    doi = _sanitize_url(entry["doi"])
    repository = pooch.create(
        path=pathlib.Path(pooch.os_cache("seareport_data")) / record / version,
        # Just here so that Pooch doesn't complain about there not being a
        # format marker in the string.
        base_url="{version}",
        version=None,
        env="SEAREPORT_DATA_DIR",
        retry_if_failed=3,
        registry={filename: entry["hashes"][filename]},
        urls={filename: doi + filename},
    )
    return repository
