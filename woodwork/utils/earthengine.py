from typing import Tuple, List
import ee
from ..auth.earthengine import authenticate_ee

if ee.data._credentials is None:
    authenticate_ee()

def get_hansen_image_from_year(year: int) -> ee.Image:
    """Get Hansen image from year.

    Returns an image wwith a single band 'loss' with values: 0 = no loss, 1 = loss in year, 2 = loss in other year

    Args:
        year (int): The year to get the Hansen image from.

    Returns:
        ee.Image: The Hansen image for the year.
    """
    
    year = ee.Number(year).subtract(2000)
    hansen = ee.Image("UMD/hansen/global_forest_change_2021_v1_9").select('lossyear')
    hansen = hansen.unmask(0)

    lossyear = hansen.eq(year)

    otherloss = ee.Image(hansen.neq(year).And(hansen.neq(0))).multiply(2)

    return lossyear.add(otherloss)

def generate_before_after_image_collections(image_collection: ee.ImageCollection, year: int) -> Tuple[ee.ImageCollection, ee.ImageCollection]:
    """Generate before and after image collections from an image collection.

    Args:
        image_collection (ee.ImageCollection): The image collection to generate the before and after image collections from.
        year (int): The year to generate the before and after image collections for.

    Returns:
        Tuple[ee.ImageCollection, ee.ImageCollection]: The before and after image collections.
    """
    before = image_collection.filterDate(f"{year-1}", f"{year}")
    after = image_collection.filterDate(f"{year+1}", f"{year+2}")

    return before, after

def generate_difference_image(before_image: ee.Image, after_image: ee.Image, hansen_image: ee.Image, change_bands: List[str]) -> ee.Image:
    """Generate a difference image from before and after images.
    
    Expects bands to be in both before and after images, the new image will have 2n + 1 bands whre n is the number of bands in the before and after images. The bands will be prefixed with 'before_' and 'after_' and the final band will be 'loss'.

    Args:
        before_image (ee.Image): The before image.
        after_image (ee.Image): The after image.
        hansen_image (ee.Image): The Hansen image.
        change_bands (List[str]): The bands to generate the difference image for.

    Returns:
        ee.Image: The difference image.
    """
    before_bands = ee.List([f"before_{band}" for band in change_bands])
    after_bands = ee.List([f"after_{band}" for band in change_bands])
    change_bands = ee.List(change_bands)

    before_image = before_image.select(change_bands, before_bands)
    after_image = after_image.select(change_bands, after_bands)

    diff = before_image.addBands(after_image, names=after_bands)
    diff = diff.addBands(hansen_image, names=ee.List(['loss'])).float()

    return diff

def export_diff_image(diff_image: ee.Image, year: int, region: ee.Geometry, scale: int, crs: str, output_path: str) -> ee.batch.Task:
    """Export a difference image to Google Drive.

    Args:
        diff_image (ee.Image): The difference image to export.
        year (int): The year the difference image is for.
        region (ee.Geometry): The region to export the difference image for.
        scale (int): The scale to export the difference image at.
        crs (str): The crs to export the difference image in.
        output_path (str): The output path to export the difference image to.
    """
    task = ee.batch.Export.image.toDrive(
        image=diff_image,
        description=f"diff_{year}_{scale}",
        folder=output_path,
        region=region,
        scale=scale,
        crs=crs,
        maxPixels=1e13,
        skipEmptyTiles=True,
        fileFormat="GeoTIFF",
        fileDimensions=512
    )
    task.start()

    return task