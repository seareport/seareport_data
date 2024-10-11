from __future__ import annotations

import importlib.resources
import inspect
import json
import logging
import os
import pathlib
import shutil
import sys
import typing as T
import zipfile

import httpx
import platformdirs
import stamina
import xxhash
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/72832981/592289
# 1. Use `eval_str=True` in order to allow `from __future__ import annotations`
# 2. Change the order somewhat in order to make it faster
def enforce_literals(function: T.Callable[..., T.Any]) -> None:
    kwargs = sys._getframe(1).f_locals
    for name, type_ in inspect.get_annotations(function, eval_str=True).items():
        if T.get_origin(type_) is T.Literal:
            value = kwargs.get(name)
            options = set(T.get_args(type_))
            if name in kwargs and value not in options:
                raise ValueError(f"Wrong value for '{name}': '{value}' is not in {options}")


def resolve_httpx_client(client: httpx.Client | None = None) -> httpx.Client:
    if client is None:
        timeout = httpx.Timeout(timeout=10, read=30)
        client = httpx.Client(timeout=timeout)
    return client


@stamina.retry(on=httpx.HTTPError, attempts=3)
def download(
    url: str,
    filename: os.PathLike[str] | str,
    client: httpx.Client | None = None,
) -> None:
    client = resolve_httpx_client(client=client)
    with client.stream("GET", url) as response:
        response.raise_for_status()
        with open(filename, "wb") as fd:
            total = int(response.headers["Content-Length"])
            tqdm_params = {
                "desc": url,
                "total": total,
                "miniters": 1,
                "unit": "B",
                "unit_scale": True,
                "unit_divisor": 1024,
            }
            with tqdm(**tqdm_params) as progress:
                downloaded = response.num_bytes_downloaded
                for chunk in response.iter_bytes():
                    fd.write(chunk)
                    progress.update(response.num_bytes_downloaded - downloaded)
                    downloaded = response.num_bytes_downloaded


def extract_zip(archive: os.PathLike[str] | str, filename: str, target_dir: os.PathLike[str] | str) -> None:
    logger.debug(f"Extracting {filename} to: {target_dir}")
    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extract(member=filename, path=target_dir)


def hash_file(path: os.PathLike[str] | str, chunksize: int = 2**20) -> str:
    hasher = xxhash.xxh128()
    with open(path, "rb") as fd:
        for chunk in iter(lambda: fd.read(chunksize), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def check_hash(path: os.PathLike[str] | str, expected_hash: str) -> None:
    logger.debug(f"Checking hash of: {path}")
    current_hash = hash_file(path)
    if current_hash != expected_hash:
        raise ValueError(f"hash mismatch: {current_hash} != {expected_hash}")


def get_cache_path() -> pathlib.Path:
    cache = os.environ.get(
        "SEAREPORT_DATA_DIR",
        platformdirs.user_cache_dir("seareport_data"),
    )
    cache_path = pathlib.Path(cache)
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def lenient_remove(path: os.PathLike[str] | str) -> None:
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            logger.exception("Failed to remove: %s", path)


def lenient_remove_tree(path: os.PathLike[str] | str) -> None:
    try:
        shutil.rmtree(path)
    except Exception:
        logger.exception("Failed to remove: %s", path)


def load_registry(registry_url: str | None = None) -> dict[str, dict[str, dict[str, T.Any]]]:
    if registry_url:
        registry: dict[str, T.Any] = httpx.get(registry_url, timeout=30).json()
    else:
        registry = json.load(importlib.resources.open_text("seareport_data", "registry.json"))
    return registry
