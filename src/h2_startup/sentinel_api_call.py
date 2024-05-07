import os
from datetime import datetime
from typing import Union
from sentinelsat import SentinelAPI
import click

def string_to_date(date_string: str) -> Union[datetime, None]:
    try:
        # Split the date string into year, month, and day components
        year, month, day = map(int, date_string.split('-'))
        # Create a datetime object
        date_object = datetime(year, month, day).date()
        return date_object
    except ValueError:
        # If the string format doesn't match, raise a DateFormatError
        raise AssertionError("Input string does not match the expected format 'YYYY-MM-DD'")

@click.command()
@click.option('--location_lon', help='The longitude and longitude coordinates to retrieve images on.', type=float)
@click.option('--location_lat', help='The longitude and longitude coordinates to retrieve images on.', type=float)
@click.option('--start_date',
              help="The start date to retrieve images from. Please provide it to the format 'YYYY-MM-DD'.", type=str)
@click.option('--end_date',
              help="The end date to retrieve images from. Please provide it to the format 'YYYY-MM-DD'.", type=str)
def main(location_lon: float, location_lat:float, start_date: str, end_date: str) -> None:

    start_date = string_to_date(start_date)
    end_date = string_to_date(end_date)
    location = [location_lon, location_lat]
    assert len(location) == 2, "Error with location parameter. Please provide longitude at index 0 and latitude at index 1"
    assert isinstance(location[0], float) or isinstance(location[0], int), "Error with location parameter. Please provide longitude at index 0 of type float or int"
    assert isinstance(location[1], float) or isinstance(location[1], int), "Error with location parameter. Please provide latitude at index 1 of type float or int"

    # connect to the API
    api = SentinelAPI(
        os.getenv("ACCES_USER_ID"),
        os.getenv("ACCES_PASSWORD"),
        show_progressbars=True
    )

    # search by coordinates, time, and SciHub query keywords
    products = api.query(
        "POINT({0} {1})".format(location[0], location[1]),
        date=(start_date, end_date),
        platformname="Sentinel-2",
        cloudcoverpercentage=(0, 30),
    )

    print("Query done")
    # download all results from the search
    api.download_all(products, directory_path=os.getenv("DIR_DATA_PATH"))

    # convert to Pandas DataFrame
    products_df = api.to_dataframe(products)

    # GeoJSON FeatureCollection containing footprints and metadata of the scenes
    api.to_geojson(products)

    # GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
    api.to_geodataframe(products)

    # # Get basic information about the product: its title, file size, MD5 sum, date, footprint and
    # # its download url
    # api.get_product_odata(<product_id>)

    # # Get the product's full metadata available on the server
    # api.get_product_odata(<product_id>, full=True)


if __name__ == "__main__":
    main()