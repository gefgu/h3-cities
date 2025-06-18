import streamlit as st
import tempfile
import os

st.set_page_config(page_title="H3-Cities")
st.title("H3-Cities")


@st.cache_data
def get_city_data(city_name: str, resolution: int):
    """Cached function to get city hexagon data"""
    try:
        import geopandas as gdf
        import osmnx as ox
        from h3 import h3
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
                    hexagons.extend(
                        h3.polyfill_geojson(poly.__geo_interface__, resolution)
                    )

            boundaries = [
                {"h": h, "geometry": Polygon(swap_lat_lon(h3.h3_to_geo_boundary(h)))}
                for h in hexagons
            ]
            return boundaries

        hexagons = get_city_hexagons(city_name, resolution)
        geo_df = gdf.GeoDataFrame(hexagons, crs="EPSG:4326")
        return geo_df
    except Exception as e:
        st.error(f"Error getting city data: {str(e)}")
        return None


def plot_city_hexagons(city_name: str, city):
    """Plot city hexagons with proper error handling"""
    try:
        import contextily as cx
        import matplotlib.pyplot as plt

        f, ax = plt.subplots(1, 1, dpi=100, figsize=(16, 9))

        city.plot(
            ax=ax,
            alpha=0.6,
            color="lightgray",
            edgecolor="black",
            linewidth=max(10 / len(city), 0.05),
        )

        # Add basemap with error handling
        try:
            cx.add_basemap(ax, crs=city.crs, source=cx.providers.CartoDB.Voyager)
        except Exception as e:
            st.warning(f"Could not load basemap: {str(e)}")

        plt.title(city_name)
        ax.set_axis_off()
        return f
    except Exception as e:
        st.error(f"Error creating plot: {str(e)}")
        return None


def clean_string(s: str):
    return s.replace(" ", "_").replace(",", "_")


# Main app logic
try:
    # Input controls
    city_name = st.text_input("City Name:", "Paris, France")
    resolution = st.slider("Resolution:", 5, 12, 8)

    if city_name:
        with st.spinner("Loading city data..."):
            city = get_city_data(city_name, resolution)

        if city is not None and not city.empty:
            # Create plot
            fig = plot_city_hexagons(city_name, city)

            if fig:
                st.pyplot(fig)

                # Generate GeoJSON for download
                try:
                    # Use temporary file instead of writing to root directory
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".geojson", delete=False
                    ) as tmp_file:
                        city.to_file(tmp_file.name, driver="GeoJSON")

                        # Read the file content for download
                        with open(tmp_file.name, "r") as f:
                            geojson_content = f.read()

                        # Clean up temporary file
                        os.unlink(tmp_file.name)

                        # Provide download button
                        filename = (
                            f"{clean_string(city_name)}_resolution_{resolution}.geojson"
                        )
                        st.download_button(
                            "Export GeoJSON (.geojson)",
                            geojson_content,
                            file_name=filename,
                            mime="application/geo+json",
                        )
                except Exception as e:
                    st.error(f"Error generating download file: {str(e)}")
            else:
                st.error("Could not generate plot")
        else:
            st.warning(
                "Could not find data for the specified city. Please check the city name and try again."
            )

except ImportError as e:
    st.error(f"Missing required dependencies: {str(e)}")
    st.markdown(
        """
        ### Installation Issue
        Some required packages are missing. This usually happens during deployment.
        Please try the alternative hosting option below.
        """
    )
    st.link_button(
        "H3-Cities - Hugging Spaces", "https://huggingface.co/spaces/gefgu/h3-cities"
    )

except Exception as e:
    st.error(f"An unexpected error occurred: {str(e)}")
    st.markdown(
        """
        ### Troubleshooting
        You can try: 
        - Change the parameters.
        - Refresh the page.
        - Go to an alternative hosting partner. (Click on the button below)
        """,
    )
    st.link_button(
        "H3-Cities - Hugging Spaces", "https://huggingface.co/spaces/gefgu/h3-cities"
    )
