"""An example of generating differenced hansen images for a given year and region."""

import ee
# auto initializes ee
from ..woodwork.utils import earthengine as ee_utils

# california
AOI = ee.FeatureCollection([ee.Feature(ee.Geometry.Polygon(
                [[[-125.251, 41.018],
                  [-121.559, 35.1434],
                  [-117.736, 32.404],
                  [-115.71, 32.700],
                  [-117.055, 36.1788],
                  [-119.736, 41.9890],
                  [-124.218, 42.005]]]))])

def mask_s2_clouds(image):
    """Mask clouds in Sentinel 2 imagery."""
    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return image.updateMask(mask).divide(10000)

s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(AOI) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

s2_18, s2_20 = ee_utils.generate_before_after_image_collections(s2, 2019)

s2_18 = s2_18.map(mask_s2_clouds)
s2_20 = s2_20.map(mask_s2_clouds)

hansen_19 = ee_utils.get_hansen_image_from_year(2019)

diff = ee_utils.generate_difference_image(s2_18.median(), s2_20.median(), hansen_19, ['B4', 'B3', 'B2'])

task = ee_utils.export_diff_image(diff, 2019, AOI, 10, 'EPSG:4326', 'exampleHansenOutputs')

print(task.active())
print("task status is: ", task.status())