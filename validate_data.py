#!/usr/bin/env python3
# ruff: noqa: T201
"""
Validate all seareport_data resources by downloading them.
This script downloads each resource and immediately cleans up to manage disk space.
"""
import functools
import os
import shutil
import sys
from itertools import product

import seareport_data as D


def clean_data_dir():
    """Clean up the data directory if it exists."""
    data_dir = os.environ.get("SEAREPORT_DATA_DIR")
    if data_dir and os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        return True
    return False


def generate_all_resources():
    """Generate all possible resource combinations based on supported parameters."""
    resources = {}

    gshhg_resolutions = ["crude", "low", "intermediate", "high", "full"]
    gshhg_shorelines = ["5", "6"]
    for resolution, shoreline in product(gshhg_resolutions, gshhg_shorelines):
        key = f"GSHHG {resolution} {shoreline}"
        resources[key] = lambda r=resolution, s=shoreline: D.gshhg_df(r, s)

    copernicus_datasets = ["bathy"]
    copernicus_versions = ["202511"]
    for dataset, version in product(copernicus_datasets, copernicus_versions):
        key = f"Copernicus {dataset} {version}"
        resources[key] = functools.partial(
            D.copernicus_ds,
            dataset=dataset,
            version=version,
        )

    gebco_datasets = ["ice", "sub_ice"]
    gebco_versions = ["2021", "2022", "2023", "2024", "2025"]
    for dataset, version in product(gebco_datasets, gebco_versions):
        key = f"GEBCO {dataset} {version}"
        resources[key] = lambda d=dataset, v=version: D.gebco_ds(d, v)

    osm_datasets = ["land", "ice"]
    osm_versions = ["2025-10", "2025-05", "2025-01"]
    for dataset, version in product(osm_datasets, osm_versions):
        key = f"OSM {dataset} {version}"
        resources[key] = functools.partial(
            D.osm_df,
            dataset=dataset,
            version=version,
        )

    etopo_datasets = ["bedrock", "surface", "geoid"]
    etopo_resolutions = ["30sec", "60sec"]
    etopo_versions = ["2022"]
    for dataset, resolution, version in product(etopo_datasets, etopo_resolutions, etopo_versions):
        key = f"ETOPO {dataset} {resolution} {version}"
        resources[key] = lambda d=dataset, r=resolution, v=version: D.etopo_ds(d, r, v)

    rtopo_datasets = ["bedrock", "ice_base", "ice_thickness", "surface_elevation"]
    for dataset in rtopo_datasets:
        key = f"RTOPO {dataset}"
        resources[key] = lambda d=dataset: D.rtopo_ds(d)

    # SRTM15+ - no options
    resources["SRTM15+"] = lambda: D.srtm15p_ds()

    # UTM - no options
    resources["UTM"] = lambda: D.utm_df()

    return resources


def main():
    """Main validation function."""
    data_dir = os.environ.get("SEAREPORT_DATA_DIR", "./seareport_data_temp")

    # Set the environment variable if not set
    if "SEAREPORT_DATA_DIR" not in os.environ:
        print(f"Setting SEAREPORT_DATA_DIR to: {data_dir}")
        os.environ["SEAREPORT_DATA_DIR"] = data_dir

    resources = generate_all_resources()
    for key in resources:
        print(key)

    failed = []
    succeeded = []

    print(f"Data directory: {os.environ['SEAREPORT_DATA_DIR']}")
    print(f"Total resources to validate: {len(resources)}\n")
    print("=" * 60)

    for i, (name, download_func) in enumerate(resources.items(), 1):
        print(f"\n[{i}/{len(resources)}] Downloading {name}...")

        try:
            download_func()
            print(f"✅ Successfully downloaded {name}")
            succeeded.append(name)
        except Exception as e:
            print(f"❌ Failed to download {name}: {e}")
            failed.append((name, str(e)))
        finally:
            # Try to clean up even on failure
            clean_data_dir()

    # Final cleanup
    clean_data_dir()

    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total resources: {len(resources)}")
    print(f"✅ Succeeded: {len(succeeded)}")
    print(f"❌ Failed: {len(failed)}")

    if succeeded:
        print(f"\nSuccessful downloads ({len(succeeded)}):")
        for name in succeeded:
            print(f"  ✓ {name}")

    if failed:
        print(f"\nFailed downloads ({len(failed)}):")
        for name, error in failed:
            print(f"  ✗ {name}: {error}")
        return 1
    else:
        print("\n🎉 All resources validated successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
