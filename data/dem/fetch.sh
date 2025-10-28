#!/bin/bash

# Maricopa County, AZ coordinates: approximately 32.55°N to 33.93°N, -113.33°W to -111.05°W
# This covers all of Maricopa County

echo "Using existing Phoenix-area DEM for now..."
echo "Full Maricopa County DEM requires manual download from USGS."
echo ""
echo "Current coverage: Phoenix metro (112.35°W to 111.85°W, 33.25°N to 33.75°N)"
echo "Desired coverage: Full Maricopa County (113.33°W to 111.05°W, 32.55°N to 33.93°N)"
echo ""
echo "To download full county DEM:"
echo "1. Visit: https://apps.nationalmap.gov/downloader/"
echo "2. Search for 'Maricopa County, Arizona'"
echo "3. Select 1/3 arc-second DEM"
echo "4. Download and place as dem.tif in this directory"
echo ""
echo "Or use USGS API (requires processing multiple tiles):"
echo "https://tnmaccess.nationalmap.gov/api/v1/products"

# Check if we already have a DEM
if [ -f dem.tif ]; then
    echo "✓ Using existing dem.tif"
    gdalinfo dem.tif | head -20
    exit 0
else
    echo "✗ No dem.tif found"
    exit 1
fi

if [ -f dem.tif ]; then
    echo "Success! DEM saved as dem.tif"
    gdalinfo dem.tif | head -20
    echo ""
    echo "You can now run: python tiles.py"
else
    echo "Error: Failed to create dem.tif"
    exit 1
fi
