# `seareport_data`

## Installation

```
pip install seareport_data
```

or

```
conda install -c conda-forge seareport_data
```

## Usage

```python
import seareport_data as D

# ETOPO supports datasets: "bedrock", "surface", "geoid"
# ETOPO supports version: "2022"
# ETOPO supports resolutions: "30sec" and "60sec"
D.etopo_ds("bedrock")
D.etopo_ds("surface", "60sec")
D.etopo_ds("geoid", "60sec", "2022")

# GEBCO supports datasets: "ice" and "sub_ice"
# GEBCO supports versions: "2022", "2023" and "2024"
D.gebco_ds("ice", "2022")
D.gebco_ds("ice", "2023")
D.gebco_ds("sub_ice", "2024")

# GSHHG supports resolutions: "crude", "low", "intermediate", "high", "full" and
# GSHHG supports shorelines: "5" and "6"
D.gshhg_df("low", "5")
D.gshhg_df("intermediate", "6")

# RTOPO supports datasets: "bedrock", "ice_base", "ice_thickness", "surface_elevation"
D.rtopo_ds("bedrock")
D.rtopo_ds("ice_base")
D.rtopo_ds("ice_thickness")
D.rtopo_ds("surface_elevation")

# SRTM15+ doesn't have any options
D.srtm15p_ds()

# UTM doesn't have any options
D.utm_df()

# OSM does have options (e.g. version) but they currently only accept one value so...
D.osm_df()
D.osm_df("ice")
D.osm_df("land")
D.osm_df("ice", "2025-10")
D.osm_df("land", "2025-05")

# Emodnet support is Provisional.
# The API only returns the paths to the files. There is no high level function to get the
# data in a single step
D.emodnet()
```
