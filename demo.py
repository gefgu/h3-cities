import streamlit as st

st.set_page_config(page_title="H3-Cities")
st.title("H3-Cities")

try:
    import contextily as cx
    import matplotlib.pyplot as plt
    import geopandas as gdf
    import osmnx as ox
    from h3 import h3
    from shapely.geometry import Polygon, MultiPolygon

    def clean_string(s: str):
        return s.replace(" ", "_").replace(",", "_")

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

    def plot_city_hexagons(city_name: str, city: gdf.GeoDataFrame):
        f, ax = plt.subplots(1, 1, dpi=100, figsize=(16, 9))

        city.plot(
            ax=ax,
            alpha=0.6,
            color="lightgray",
            edgecolor="black",
            linewidth=max(10 / len(city), 0.05),
        )
        cx.add_basemap(ax, crs=city.crs, source=cx.providers.CartoDB.Voyager)
        plt.title(city_name)
        ax.set_axis_off()
        return f

    city_name = st.text_input("City Name:", "Paris, France")
    resolution = st.slider("Resolution:", 5, 12, 8)

    city = get_city_hexagons_geo_df(city_name, resolution)
    fig = plot_city_hexagons(city_name, city)

    save_path = f"{clean_string(city_name)}_resolution_{resolution}.geojson"

    city.to_file(save_path, driver="GeoJSON")
    if fig:
        st.pyplot(fig)
    else:
        st.write("Sorry... We couldn't find the data you wanted :(")
    with open(save_path, "rb") as f:
        st.download_button("Export GeoJSON (.geojson)", f, file_name=save_path)
except:
    st.text("Something Went Wrong!!!")
    st.markdown(
        """
        You can try: 
        - Change the parameters.
        - Refresh the page.
        - Go to an alternative hosting partner. (Click on the button below)
        """,
    )
    st.link_button(
        "H3-Cities - Hugging Spaces", "https://huggingface.co/spaces/gefgu/h3-cities"
    )
