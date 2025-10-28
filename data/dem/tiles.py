import os
import whitebox
from osgeo import gdal
import numpy as np

# Initialize WhiteboxTools
wbt = whitebox.WhiteboxTools()

def delineate_basins(dem_path, output_dir, flow_accum_threshold, max_influence_distance):
    """
    Delineate basins from a DEM and create water accumulation visualization

    Parameters:
    dem_path (str): Path to input DEM file
    output_dir (str): Directory to save output files
    flow_accum_threshold (int): Threshold for stream extraction (lower for desert = more sensitive)
    max_influence_distance (float): Distance for influence calculation
    """
    os.makedirs(output_dir, exist_ok=True)

    # Define output paths
    filled_dem = os.path.join(output_dir, "filled_dem.tif")
    flow_accum = os.path.join(output_dir, "flow_accum.tif")
    flow_dir = os.path.join(output_dir, "flow_dir.tif")
    streams = os.path.join(output_dir, "streams.tif")
    influence = os.path.join(output_dir, "stream_influence.tif")

    # Fill depressions in DEM
    print("Filling depressions...")
    wbt.fill_depressions(dem_path, filled_dem)

    # Calculate flow direction
    print("Calculating flow direction...")
    wbt.d8_pointer(filled_dem, flow_dir)

    # Calculate flow accumulation
    print("Calculating flow accumulation...")
    wbt.d8_flow_accumulation(filled_dem, flow_accum)

    # Extract streams (lower threshold for Phoenix desert hydrology)
    print(f"Extracting streams with threshold {flow_accum_threshold}...")
    wbt.extract_streams(flow_accum, streams, threshold=flow_accum_threshold)

    # Calculate influence areas
    print("Calculating stream influence...")
    wbt.gaussian_filter(
        flow_accum,
        influence,
        sigma=max_influence_distance/4
    )

    # Get natural log of influence areas
    print("Calculating natural log of stream influence...")
    wbt.ln(influence, influence)

    # Standard deviation contrast stretch
    print("Calculating standard deviation contrast stretch...")
    wbt.standard_deviation_contrast_stretch(
        influence,
        influence,
        stdev=2,
        num_tones=3
    )

    # Rescale to 1-4 range for visualization
    print("Rescaling influence...")
    wbt.rescale_value_range(
        influence,
        influence,
        out_min_val=1,
        out_max_val=4
    )

    print(f"Analysis complete! Results saved to: {output_dir}")
    return influence

def reclassify_influence_raster(input_file, output_file, num_classes=4):
    """
    Reclassify the influence raster using GDAL
    """
    src_ds = gdal.Open(input_file)
    src_band = src_ds.GetRasterBand(1)
    src_data = src_band.ReadAsArray()

    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(output_file,
                          src_ds.RasterXSize,
                          src_ds.RasterYSize,
                          1,
                          gdal.GDT_Byte)

    dst_ds.SetProjection(src_ds.GetProjection())
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())

    min_val = 1
    max_val = 4
    interval = (max_val - min_val) / num_classes

    dst_data = np.zeros_like(src_data, dtype=np.uint8)

    for i in range(num_classes):
        lower = min_val + (i * interval)
        upper = min_val + ((i + 1) * interval)

        if i == 0:
            mask = (src_data >= lower) & (src_data <= upper)
        else:
            mask = (src_data > lower) & (src_data <= upper)

        dst_data[mask] = i + 1

    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(dst_data)
    dst_band.SetNoDataValue(0)

    src_ds = None
    dst_ds = None

    return output_file

def convert_raster_to_vector(input_raster, output_vector):
    """
    Convert a raster file to vector format using WhiteboxTools
    """
    wbt.set_nodata_value(
        input_raster,
        input_raster,
        back_value=1,
    )

    wbt.raster_to_vector_polygons(input_raster, output_vector)
    return output_vector

if __name__ == "__main__":
    pwd = os.getcwd()
    dem_path = os.path.join(pwd, "dem.tif")
    output_dir = os.path.join(pwd, "tiles")

    # Phoenix desert hydrology parameters:
    # - Lower flow accumulation threshold (500 instead of 1000)
    # - Influence distance of 1
    print("Starting Phoenix water accumulation analysis...")
    print("Note: Using desert-adapted parameters")

    delineate_basins(dem_path, output_dir, 500, 1)

    # Reclassify influence
    print("Reclassifying influence...")
    input_file = os.path.join(output_dir, "stream_influence.tif")
    output_file = os.path.join(output_dir, "stream_influence_reclass.tif")
    reclassify_influence_raster(input_file, output_file, num_classes=4)

    # Convert to vector
    print("Converting to vector format...")
    vector_file = os.path.join(output_dir, "stream_influence_reclass.shp")
    convert_raster_to_vector(output_file, vector_file)

    print("\nAnalysis complete!")
    print(f"Vector output: {vector_file}")
    print("\nNext step: Convert the shapefile to PMTiles using tippecanoe")
