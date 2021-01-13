# Satellite CZML

Creates a CZML string based on TLE (Two Line Element set) data for plotting satellites on the open source [CesiumJS](https://cesium.com/cesiumjs/) JavaScript library.  A CZML file/string is used by CesiumJS to show a Time Animation such as in this [example](https://sandcastle.cesium.com/?src=CZML.html).

## Installation

`pip install satellite_czml`

## Usage

This library contains two classes that can be used to generate a CZML string.

- 


## Thank You

Special thanks to Shane Carty and Christian Ledermann for your initial work which made this work possible.

This is based on Shane Carty's (@kujosHeist) [tle2czml](https://github.com/kujosHeist/tle2czml) python package and uses his motified version of `czml.py` from Christian Ledermann.

Also thanks to Christian Ledermann for his [czml](https://github.com/cleder/czml) python package for the the heavy lifting.
