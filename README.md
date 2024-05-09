# Sentinel Hub API

The main goal is to retrieve images from Sentinel-2 Level 2A using the [Sentinel Hub API](https://www.sentinel-hub.com/). We want to have a pyton script that requests the API in order to download the images that we want, given a location and a timeframe.

**Constraints:**

- Language: Python.
- Expected file: Python file(s) or jupyter notebook (would prefer the former).
- Function inputs: Coordinates for a **location**, as well as a **start dates** and **end dates**.
- Expected output: Downloads all of the images for that location at those dates to a specific folder (cf the .env section).
- The **location** will be given as a list of coordinates, and the **dates** will be inputed as strings in the format expected by the API, but it would be good to add failsafes incase the input isn't formatted the right way.

**Allowed:**

- Can import any and all necessary libraries.
- Can assume that the user has a proper .env with the two following variables: the access token for the API, as well as the path to the folder for the images. Feel free to name both variables as you see fit, and to add more variables if needed.
- Can assume that the user has the same versions of Python and libraries as you.

That's all! Have a good day.

**Solution Run Command**
You can run the script using the command line :

```console
python3 /workspace/src/h2_startup/sentinel_api_call_sentinelhub.py --location_lon 31.625 --location_lat 34.665 --start_date "2022-01-20" --end_date "2022-01-25"
```

**Details**
It only requires longitude and latitude coordinates. The next step would be to request the min_lon, min_lat, max_lon and max_lat coordinates bbox.
