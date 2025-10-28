#!/usr/bin/env python3
"""
Download USGS DEM data for Maricopa County using USGS API
API Key: Ubx2JcufxFavWpxsg5Nu8uYsxiL7KnyYnSDToBfd
"""

import requests
import json
import subprocess
import os

# USGS API Key
USGS_API_KEY = "Ubx2JcufxFavWpxsg5Nu8uYsxiL7KnyYnSDToBfd"

# Maricopa County bounds
MARICOPA_BOUNDS = {
    "min_lon": -113.33,
    "max_lon": -111.05,
    "min_lat": 32.55,
    "max_lat": 33.93
}

def search_usgs_dem():
    """
    Search USGS National Map for DEM products covering Maricopa County
    """
    print("Searching USGS National Map for DEM products...")

    # USGS TNM API endpoint
    url = "https://tnmaccess.nationalmap.gov/api/v1/products"

    params = {
        "bbox": f"{MARICOPA_BOUNDS['min_lon']},{MARICOPA_BOUNDS['min_lat']},{MARICOPA_BOUNDS['max_lon']},{MARICOPA_BOUNDS['max_lat']}",
        "datasets": "National Elevation Dataset (NED) 1/3 arc-second",
        "prodFormats": "GeoTIFF",
        "outputFormat": "JSON",
        "max": 100
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            print(f"✓ Found {len(data['items'])} DEM products")
            return data["items"]
        else:
            print("⚠ No DEM products found")
            return []

    except Exception as e:
        print(f"✗ API search failed: {e}")
        return []


def download_dem_tiles(products):
    """
    Download DEM tiles from USGS
    """
    print("\nDownloading DEM tiles...")

    downloaded_files = []

    for i, product in enumerate(products[:10]):  # Limit to 10 tiles
        title = product.get("title", f"tile_{i}")
        download_url = product.get("downloadURL")

        if not download_url:
            continue

        # Clean filename
        filename = title.replace(" ", "_").replace("/", "_") + ".tif"

        print(f"\n  [{i+1}/{min(10, len(products))}] {title}")
        print(f"  URL: {download_url[:80]}...")

        try:
            response = requests.get(download_url, stream=True, timeout=120)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(filename, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_size) * 100
                        print(f"\r  Progress: {percent:.1f}%", end='', flush=True)

            print(f"\r  ✓ Downloaded: {filename}")
            downloaded_files.append(filename)

        except Exception as e:
            print(f"\r  ✗ Failed: {e}")
            continue

    return downloaded_files


def merge_and_clip_tiles(tile_files):
    """
    Merge DEM tiles and clip to Maricopa County bounds
    """
    if not tile_files:
        print("\n✗ No tiles to merge")
        return False

    print(f"\nMerging {len(tile_files)} tiles...")

    try:
        # Build VRT from all tiles
        print("  Creating virtual raster...")
        subprocess.run(
            ["gdalbuildvrt", "temp_maricopa.vrt"] + tile_files,
            check=True
        )

        # Clip to Maricopa County bounds
        print("  Clipping to Maricopa County bounds...")
        subprocess.run([
            "gdal_translate",
            "-projwin",
            str(MARICOPA_BOUNDS['min_lon']),
            str(MARICOPA_BOUNDS['max_lat']),
            str(MARICOPA_BOUNDS['max_lon']),
            str(MARICOPA_BOUNDS['min_lat']),
            "temp_maricopa.vrt",
            "dem.tif"
        ], check=True)

        # Clean up
        print("  Cleaning up...")
        os.remove("temp_maricopa.vrt")
        for tile in tile_files:
            if os.path.exists(tile):
                os.remove(tile)

        print("\n✓ Success! DEM saved as dem.tif")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("USGS DEM Downloader for Maricopa County")
    print("=" * 60)

    products = search_usgs_dem()

    if not products:
        print("\n⚠ No products found")
        return

    downloaded = download_dem_tiles(products)

    if not downloaded:
        print("\n✗ No tiles downloaded")
        return

    success = merge_and_clip_tiles(downloaded)

    if success:
        print("\n✓ Ready to run: python tiles.py")


if __name__ == "__main__":
    main()
