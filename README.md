# `seareport_data`

## Installation

```
pip install seareport_data
```

## Usage

```
import seareport_data as D

# ETOPO supports datasets: "bedrock", "surface", "geoid"
# ETOPO supports version: "2022"
# ETOPO supports resolutions: "30sec" and "60sec"
D.etopo_ds("bedrock")
D.etopo_ds("surface", "60sec")
D.etopo_ds("geoid", "60sec", "2022)

# GEBCO supports datasets: "ice" and "sub_ice"
# GEBCO supports versions: "2023" and "2024"
D.gebco_ds("ice", "2023")
D.gebco_ds("sub_ice", "2024")

# GSSHG supports resolutions: "crude", "low", "intermediate", "high", "full" and
# GSSHG supports shorelines: "5" and "6"
D.gsshg_df("low", "6")
D.gsshg_df("low", "6")

# RTOPO supports datasets: "bedrock", "ice_base", "ice_thickness", "surface_elevation"
D.rtopo_ds("bedrock")
D.rtopo_ds("ice_base")
D.rtopo_ds("ice_thickness")
D.rtopo_ds("surface_elevation")

# SRTM15+ doesn't have any options
D.srtm15p_ds()

# UTM doesn't have any options
D.utm_df()
```
