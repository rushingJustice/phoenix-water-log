#!/bin/bash

# Generate PMTiles from the processed raster

echo "Generating PMTiles from water accumulation data..."

# Input GeoTIFF from tiles.py output
INPUT_TIFF="../dem/tiles/stream_influence_reclass.tif"
TEMP_GEOJSON="temp_polygons.geojson"
OUTPUT_FILE="../../static/tiles.pmtiles"

# Check if input file exists
if [ ! -f "$INPUT_TIFF" ]; then
    echo "Error: Input file $INPUT_TIFF not found!"
    echo "Please run tiles.py first to generate the raster."
    exit 1
fi

# Convert raster to GeoJSON polygons using gdal_polygonize
echo "Converting raster to GeoJSON..."
gdal_polygonize.py "$INPUT_TIFF" -f "GeoJSON" "$TEMP_GEOJSON" VALUE VALUE

# Check if GeoJSON was created
if [ ! -f "$TEMP_GEOJSON" ]; then
    echo "Error: Failed to create GeoJSON"
    exit 1
fi

# Generate PMTiles using tippecanoe
echo "Generating PMTiles with higher resolution..."
tippecanoe \
  -o "$OUTPUT_FILE" \
  -z 15 \
  --force \
  --drop-densest-as-needed \
  --no-tile-compression \
  --layer="stream_influence_water_difference" \
  "$TEMP_GEOJSON"

# Clean up
rm -f "$TEMP_GEOJSON"

echo "Done! PMTiles generated at $OUTPUT_FILE"
echo "You can now run 'npm run dev' to see the map"
