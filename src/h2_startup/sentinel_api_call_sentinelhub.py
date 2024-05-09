import os
from datetime import datetime
from typing import Union

import click
from sentinelhub import SHConfig
from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    SentinelHubRequest,
    bbox_to_dimensions,
)


def string_to_date(date_string: str) -> Union[datetime, None]:
    try:
        # Split the date string into year, month, and day components
        year, month, day = map(int, date_string.split("-"))
        # Create a datetime object
        date_object = datetime(year, month, day).date()
        # return date_object
    except ValueError:
        # If the string format doesn't match, raise a DateFormatError
        raise AssertionError(
            "Input string does not match the expected format 'YYYY-MM-DD'"
        )


@click.command()
@click.option(
    "--location_lon",
    help="The longitude and longitude coordinates to retrieve images on.",
    type=float,
)
@click.option(
    "--location_lat",
    help="The longitude and longitude coordinates to retrieve images on.",
    type=float,
)
@click.option(
    "--start_date",
    help="The start date to retrieve images from. Please provide it to the format 'YYYY-MM-DD'.",
    type=str,
)
@click.option(
    "--end_date",
    help="The end date to retrieve images from. Please provide it to the format 'YYYY-MM-DD'.",
    type=str,
)
def main(
    location_lon: float, location_lat: float, start_date: str, end_date: str
) -> None:
    string_to_date(start_date)
    string_to_date(end_date)
    location = [location_lon, location_lat]
    assert (
        len(location) == 2
    ), "Error with location parameter. Please provide longitude at index 0 and latitude at index 1"
    assert isinstance(location[0], float) or isinstance(
        location[0], int
    ), "Error with location parameter. Please provide longitude at index 0 of type float or int"
    assert isinstance(location[1], float) or isinstance(
        location[1], int
    ), "Error with location parameter. Please provide latitude at index 1 of type float or int"

    config = SHConfig()

    if not config.sh_client_id or not config.sh_client_secret:
        print("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")

    image_coords_wgs84 = (location_lon-0.5, location_lat-0.5, location_lon+0.5, location_lat+0.5)

    resolution = 60
    betsiboka_bbox = BBox(bbox=image_coords_wgs84, crs=CRS.WGS84)
    betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

    print(f"Image shape at {resolution} m resolution: {betsiboka_size} pixels")

    evalscript_true_color = """
        //VERSION=3

        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04"]
                }],
                output: {
                    bands: 3
                }
            };
        }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
    """

    request_true_color = SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(start_date, end_date),
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=betsiboka_bbox,
        size=betsiboka_size,
        config=config,
        data_folder=os.getenv("DIR_DATA_PATH")
    )

    true_color_imgs = request_true_color.get_data()

    print(f"Saving data to {os.getenv('DIR_DATA_PATH')}")
    request_true_color.save_data()

if __name__ == "__main__":
    main()
