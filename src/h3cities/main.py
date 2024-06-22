import osmnx as ox
from h3 import h3
import geopandas as gdf
from shapely.geometry import Polygon, MultiPolygon


def swap_lat_lon(coords):
    return [(lat, lon) for lon, lat in coords]


def get_city_hexagons(city_name: str, resolution: int):
    if not isinstance(resolution, int) or resolution < 0 or resolution > 15:
        raise ValueError("resolution must be an integer between 0 and 15.")
    if not isinstance(city_name, str):
        raise ValueError("city_name must be an string")
    city = ox.geocode_to_gdf(city_name)
    if not isinstance(city, gdf.GeoDataFrame):
        raise ValueError("City not found by Open Street Map")

    geometry = city["geometry"][0]
    if isinstance(geometry, Polygon):
        hexagons = h3.polyfill_geojson(geometry.__geo_interface__, resolution)
    elif isinstance(geometry, MultiPolygon):
        hexagons = []
        for poly in geometry.geoms:
            hexagons.extend(h3.polyfill_geojson(poly.__geo_interface__, resolution))
    boundaries = [
        {"h": h, "geometry": Polygon(swap_lat_lon(h3.h3_to_geo_boundary(h)))}
        for h in hexagons
    ]
    return boundaries


def get_city_hexagons_geo_df(city_name: str, resolution: int):
    hexagons = get_city_hexagons(city_name, resolution)
    geo_df = gdf.GeoDataFrame(hexagons, crs="EPSG:4326")
    return geo_df
