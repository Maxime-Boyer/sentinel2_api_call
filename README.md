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

**Problem with the connection**
For now, I'm having a problem connecting to apihub.copernicus.eu through the api. I have registered and called the api using the correct username and password.

With the vpn turned on, I get the error :

<!-- language: none -->

    requests.exceptions.ConnectionError: HTTPSConnectionPool(host='apihub.copernicus.eu', port=443): Max retries exceeded with url: /apihub/search?format=json&rows=100&start=0&q=beginPosition%3A%5B%222022-01-20T00%3A00%3A00Z%22+TO+%222022-03-20T00%3A00%3A00Z%22%5D+cloudcoverpercentage%3A%5B%220%22+TO+%2230%22%5D+platformname%3A%22Sentinel-2%22+footprint%3A%22Intersects%28POINT%2834.665+31.625%29%29%22 (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0xffffb2923fd0>: Failed to establish a new connection: [Errno 111] Connection refused'))

With the vpn turned off, I get the error :

<!-- language: none -->

    requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

**Run**
You can run the script using the command line :

```console
python3 /workspace/src/h2_startup/sentinel_api_call.py --location_lon 31.625 --location_lat 34.665 --start_date "2022-01-20" --end_date "2022-01-25"
```
